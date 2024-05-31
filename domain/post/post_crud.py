from datetime import datetime
import math
from typing import Optional

from fastapi import HTTPException
from domain.post.post_schema import PostCreate, PostUpdate
from domain.user import user_crud
from models import Post, User, Board, Comment, Image, Notification, PostCategory
from sqlalchemy.orm import Session
from sqlalchemy import or_
from utils import file_utils
from firebase_admin import messaging


def get_post_list(db: Session, board_id: int = 0, start_index: int = 0, limit: int = 10,
                  category: PostCategory = None, is_hot: bool = False, search_keyword: str = None, sort_order: str = 'latest'):
    query = db.query(Post)
    if board_id != 0:
        query = query.filter(Post.board_id == board_id)
    if is_hot:
        query = query.filter(Post.is_hot == True)
    if category:
        query = query.filter(Post.category == category)
    if search_keyword:
        keyword_filter = or_(Post.subject.ilike(f"%{search_keyword}%"), Post.content.ilike(f"%{search_keyword}%"))
        query = query.filter(keyword_filter)

    if sort_order == 'oldest':
        query = query.order_by(Post.create_date.asc())
    elif sort_order == 'popularity':
        query = query.order_by(Post.like_count.desc())
    else:
        query = query.order_by(Post.create_date.desc())

    total = query.count()
    total_pages = math.ceil(total / limit)

    _post_list = query.offset(start_index).limit(limit).all()

    for post in _post_list:
        post.comment_count = db.query(Comment).filter(Comment.post_id == post.id).count()
    return total_pages, _post_list


def get_my_post_list(db: Session, user: User, start_index: int = 0, limit: int = 10):
    query = db.query(Post).filter(Post.user_id == user.id)

    query = query.order_by(Post.create_date.desc())

    total = query.count()
    total_pages = math.ceil(total / limit)

    my_post_list = query.offset(start_index).limit(limit).all()

    for post in my_post_list:
        post.comment_count = db.query(Comment).filter(Comment.post_id == post.id).count()
    return total_pages, my_post_list


def get_post(db: Session, post_id: int, start_index: int = 0, limit: int = 10, sort_order: str = 'latest'):
    post = db.query(Post).get(post_id)

    comment_map = {}
    sub_comments_count = {}

    top_level_comments = []

    for comment in post.comment_posts:
        comment.sub_comments = []
        comment_map[comment.id] = comment

        if comment.parent_id is None:
            comment.sub_comments_count = 0
            top_level_comments.append(comment)
            comment_map[comment.id] = top_level_comments[-1]
        else:
            if comment.parent_id in sub_comments_count:
                sub_comments_count[comment.parent_id] += 1
            else:
                sub_comments_count[comment.parent_id] = 1

    # Sort the comments based on the sort_order parameter
    if sort_order == 'oldest':
        top_level_comments.sort(key=lambda x: x.create_date)
    elif sort_order == 'popularity':
        top_level_comments.sort(key=lambda x: x.like_count, reverse=True)
    else:
        top_level_comments.sort(key=lambda x: x.create_date, reverse=True)

    # Ensure all comments are included in the range
    if start_index + limit > len(top_level_comments):
        limit = len(top_level_comments) - start_index

    paginated_comments = top_level_comments[start_index:start_index + limit]

    for comment in paginated_comments:
        if comment.id in sub_comments_count:
            comment.sub_comments_count = sub_comments_count[comment.id]

    post.comment_posts = paginated_comments
    post.comment_count = db.query(Comment).filter(Comment.post_id == post.id).count()

    total_comments = len(top_level_comments)
    total_pages = math.ceil(total_comments / limit) if limit > 0 else 0
    return total_pages, post


def get_post_by_post_id(db: Session, post_id: int):
    return db.query(Post).get(post_id)


def get_post_author(db: Session, post_id: int):
    post = db.query(Post).get(post_id)
    return post.user


def get_image_by_post_id(db: Session, post_id: int):
    return db.query(Image).filter(Image.post_id == post_id).all()


def get_image_by_hash(db: Session, image_hash: str):
    return db.query(Image).filter(Image.image_hash == image_hash).first()


def get_image_by_hash_all(db: Session, image_hash: str):
    return db.query(Image).filter(Image.image_hash == image_hash).all()


def create_post(db: Session, post_create: PostCreate, board: Board, user: User):
    user_crud.add_user_activity_and_points(db, user=user, activity_type='post', activity_limit=10,
                                           activity_point=5)

    db_post = Post(board=board,
                   subject=post_create.subject,
                   content=post_create.content,
                   category=post_create.category,
                   is_anonymous=post_create.is_anonymous,
                   create_date=datetime.now(),
                   user=user)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    unique_images = {img.image_hash: img for img in post_create.images_post}.values()

    for image in unique_images:
        db_image = Image(image_url=image.image_url, image_hash=image.image_hash, post_id=db_post.id)
        db.add(db_image)

    db.commit()


def update_post(db: Session, db_post: Post, post_update: PostUpdate):
    db_post.subject = post_update.subject
    db_post.content = post_update.content
    db_post.category = post_update.category
    db_post.is_anonymous = post_update.is_anonymous
    db_post.modify_date = datetime.now()
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    current_images = get_image_by_post_id(db, post_id=db_post.id)
    submitted_images = post_update.images_post

    # 중복 이미지 해시 제거 (동일한 image_hash를 가진 이미지는 하나만 남김)
    unique_submitted_images = {img.image_hash: img for img in submitted_images}.values()

    current_image_hashes = {img.image_hash for img in current_images}
    submitted_image_hashes = {img.image_hash for img in unique_submitted_images}

    # 삭제할 이미지 결정
    for now_image in current_images:
        if now_image.image_hash not in submitted_image_hashes:
            # 다른 게시글에서 사용 중인 이미지는 저장소에서 삭제하지 않음
            other_images = get_image_by_hash_all(db, image_hash=now_image.image_hash)
            if any(image.post_id != db_post.id for image in other_images):
                db.delete(now_image)
                continue

            # 데이터베이스에서 이미지 존재 여부 확인
            image_in_db = db.query(Image).filter(Image.id == now_image.id).first()
            if image_in_db is None:
                continue

            # 이미지 파일 삭제 시도
            try:
                file_utils.delete_image_file(now_image.image_url)
            except Exception as e:
                print(f"Failed to delete image file: {e}")
            else:
                db.delete(now_image)

    # 새로운 이미지 추가
    for image in unique_submitted_images:
        if image.image_hash not in current_image_hashes:
            db_image = Image(image_url=image.image_url, image_hash=image.image_hash, post_id=db_post.id)
            db.add(db_image)

    db.commit()


def delete_post(db: Session, db_post: Post):
    images = get_image_by_post_id(db, post_id=db_post.id)
    for image in images:
        # 이미지가 다른 게시글에서 사용중이면 저장소에서는 삭제 X
        other_image = get_image_by_hash(db, image_hash=image.image_hash)
        if other_image and other_image.post_id != db_post.id:
            db.delete(image)
            continue

        file_utils.delete_image_file(image.image_url)
        db.delete(image)

    if db_post.user.point >= 5:
        db_post.user.point -= 5
    elif db_post.user.point < 5:
        db_post.user.point = 0

    db.delete(db_post)
    db.commit()


HOT_STATUS_UPDATE_CRITERIA = {
    3: (1, 2),
    4: (7, 6),
    5: (5, 5),
    6: (5, 5),
    7: (5, 5),
    8: (5, 5),
    9: (5, 5),
    10: (5, 5),
    11: (8, 10),
    12: (5, 5),
    13: (8, 7),
    14: (7, 6),
    16: (8, 10),
    17: (8, 10),
    18: (10, 6),
    19: (5, 6),
}


def get_hot_message_title(language_preference: str, message_type: str):
    titles = {
        'hot_selected': {
            '한국어': '🔥 내 게시글이 베스트로 선정되었어요.',
            'English': '🔥 Your post has been selected as a Best Post.',
            # Add more languages here
        },
    }

    return titles[message_type].get(language_preference, titles[message_type]['English'])


def update_hot_status(db: Session, post_id: int):
    # Get the post from the database
    post = db.query(Post).filter(Post.id == post_id).first()

    # Check if the post exists
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.is_hot:
        return

    if post.board_id == 15:
        return

    # Get the number of unique users who commented on the post
    comment_user_count = len(set(comment.user_id for comment in db.query(Comment).filter(Comment.post_id == post_id).all()))

    criteria = HOT_STATUS_UPDATE_CRITERIA.get(post.board_id, (5, 5))
    min_likes, min_comment_users = criteria

    # Update the is_hot status if the conditions are met
    if post.like_count >= min_likes or comment_user_count >= min_comment_users:
        post.is_hot = True
        post.user.point += 50

        db_notification = Notification(translation_key='bestPostSelected',
                                       title='',
                                       body=post.subject,
                                       post_id=post.id,
                                       create_date=datetime.now(),
                                       is_Post=True,
                                       user_id=post.user_id)
        db.add(db_notification)

        title = get_hot_message_title(language_preference=post.user.language_preference, message_type='hot_selected')

        # Add push notification sending here
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=post.subject,
            ),
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    sound='default'
                )
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound='default',
                        content_available=True
                    )
                )
            ),
            token=post.user.fcm_token  # Assuming the User model has an fcm_token field
        )

        messaging.send(message)

    db.commit()
