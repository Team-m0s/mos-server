from datetime import datetime

from domain.post.post_schema import PostCreate, PostUpdate
from models import Post, User, Board, Comment, Image
from sqlalchemy.orm import Session
from sqlalchemy import or_
from utils import file_utils
import domain.accompany.accompany_crud


def get_post_list(db: Session, board_id: int = 0, start_index: int = 0, limit: int = 10,
                  search_keyword: str = None, sort_order: str = 'latest'):
    query = db.query(Post)
    if board_id != 0:
        query = query.filter(Post.board_id == board_id)
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
    _post_list = query.offset(start_index).limit(limit).all()

    for post in _post_list:
        post.comment_count = db.query(Comment).filter(Comment.post_id == post.id).count()
    return total, _post_list


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

    # Apply pagination to the sorted comments
    paginated_comments = top_level_comments[start_index:start_index + limit]

    for comment in paginated_comments:
        if comment.id in sub_comments_count:
            comment.sub_comments_count = sub_comments_count[comment.id]

    post.comment_posts = paginated_comments
    return post


def get_image_by_post_id(db: Session, post_id: int):
    return db.query(Image).filter(Image.post_id == post_id).all()


def get_image_by_hash(db: Session, image_hash: str):
    return db.query(Image).filter(Image.image_hash == image_hash).first()


def get_image_by_hash_all(db: Session, image_hash: str):
    return db.query(Image).filter(Image.image_hash == image_hash).all()


def create_post(db: Session, post_create: PostCreate, board: Board, user: User):
    db_post = Post(board=board,
                   subject=post_create.subject,
                   content=post_create.content,
                   is_anonymous=post_create.is_anonymous,
                   create_date=datetime.now(),
                   user=user)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    for image in post_create.images_post:
        db_image = Image(image_url=image.image_url, image_hash=image.image_hash, post_id=db_post.id)
        db.add(db_image)

    user.point += 5
    db.commit()


def update_post(db: Session, db_post: Post, post_update: PostUpdate):
    db_post.subject = post_update.subject
    db_post.content = post_update.content
    db_post.is_anonymous = post_update.is_anonymous
    db_post.modify_date = datetime.now()
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    current_images = get_image_by_post_id(db, post_id=db_post.id)
    submitted_images = post_update.images_post

    # 이미지 해시 세트 생성
    current_image_hashes = {img.image_hash for img in current_images}
    submitted_image_hashes = {img.image_hash for img in submitted_images}

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
    for image in submitted_images:
        if image.image_hash not in current_image_hashes:
            db_image = Image(image_url=image.image_url, image_hash=image.image_hash, post_id=db_post.id)
            db.add(db_image)

    db.commit()


def delete_post(db: Session, db_post: Post):
    images = get_image_by_post_id(db, post_id=db_post.id)
    for image in images:
        #이미지가 다른 게시글에서 사용중이면 저장소에서는 삭제 X
        other_image = get_image_by_hash(db, image_hash=image.image_hash)
        if other_image and other_image.post_id != db_post.id:
            db.delete(image)
            continue

        file_utils.delete_image_file(image.image_url)
        db.delete(image)
    db.delete(db_post)
    db.commit()
