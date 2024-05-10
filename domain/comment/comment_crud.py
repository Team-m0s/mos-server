import math
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from domain.comment.comment_schema import CommentCreate, CommentUpdate, CommentDelete, SubCommentCreate, \
    NoticeCommentCreate, VocaCommentCreate
from domain.post import post_crud
from domain.user import user_crud

from models import Post, Comment, User, Notice, Notification, BestComment, Vocabulary


def create_comment(db: Session, post: Post, comment_create: CommentCreate, user: User):
    user_crud.add_user_activity_and_points(db, user=user, activity_type='comment', activity_limit=30,
                                           activity_point=2)

    db_comment = Comment(post=post,
                         content=comment_create.content,
                         is_anonymous=comment_create.is_anonymous,
                         create_date=datetime.now(),
                         user=user)
    db.add(db_comment)

    if post.user_id != user.id:
        db_notification = Notification(title=f'내 게시글 "{post.subject}"에 새로운 댓글이 달렸어요.',
                                       body=comment_create.content,
                                       post_id=post.id,
                                       create_date=datetime.now(),
                                       is_Post=True,
                                       user_id=post.user_id)

        db.add(db_notification)

    db.commit()
    db.refresh(db_comment)

    post_crud.update_hot_status(db, post.id)
    return db_comment


def create_sub_comment(db: Session, comment: Comment, sub_comment_create: SubCommentCreate, user: User):
    user_crud.add_user_activity_and_points(db, user=user, activity_type='comment', activity_limit=30,
                                           activity_point=2)

    db_sub_comment = Comment(post=comment.post,
                             parent_id=comment.id,
                             content=sub_comment_create.content,
                             is_anonymous=sub_comment_create.is_anonymous,
                             create_date=datetime.now(),
                             user=user)
    db.add(db_sub_comment)

    if comment.user_id != user.id:
        db_notification = Notification(title=f'내 댓글 "{comment.content}"에 새로운 답글이 달렸어요.',
                                       body=sub_comment_create.content,
                                       post_id=comment.post_id,
                                       create_date=datetime.now(),
                                       is_Post=True,
                                       user_id=comment.user_id)

        db.add(db_notification)

    db.commit()
    db.refresh(db_sub_comment)

    post_crud.update_hot_status(db, comment.post_id)
    return db_sub_comment


def create_notice_comment(db: Session, notice: Notice, notice_comment_create: NoticeCommentCreate, user: User):
    db_notice_comment = Comment(notice=notice,
                                content=notice_comment_create.content,
                                is_anonymous=False,
                                create_date=datetime.now(),
                                user=user)
    db.add(db_notice_comment)
    db.commit()
    db.refresh(db_notice_comment)
    return db_notice_comment


def create_vocabulary_comment(db: Session, vocabulary: Vocabulary, voca_comment_create: VocaCommentCreate, user: User):
    user_crud.add_user_activity_and_points(db, user=user, activity_type='comment', activity_limit=0,
                                           activity_point=2)

    db_voca_comment = Comment(vocabulary=vocabulary,
                              content=voca_comment_create.content,
                              create_date=datetime.now(),
                              user=user)
    db.add(db_voca_comment)
    db.commit()
    db.refresh(db_voca_comment)
    return db_voca_comment


def get_comment_by_id(db: Session, comment_id: int):
    comment = db.query(Comment).get(comment_id)
    if comment:
        comment.sub_comments_count = db.query(Comment).filter(Comment.parent_id == comment.id).count()
    return comment


def get_my_commented_posts(db: Session, user: User, start_index: int = 0, limit: int = 10):
    # Query to get all comments made by the user
    user_comments_query = db.query(Comment).filter(Comment.user_id == user.id)

    # Get all unique posts associated with these comments
    post_ids = {comment.post_id for comment in user_comments_query.all()}

    # Query to get these posts
    query = db.query(Post).filter(Post.id.in_(post_ids))

    # Order by creation date and apply pagination
    query = query.order_by(Post.create_date.desc())
    total = query.count()
    total_pages = math.ceil(total / limit)
    my_commented_posts = query.offset(start_index).limit(limit).all()

    for post in my_commented_posts:
        post.comment_count = db.query(Comment).filter(Comment.post_id == post.id).count()
        post.total_pages = total_pages

    return total_pages, my_commented_posts


def get_post_comment_count(db: Session, post_id: int):
    return db.query(Comment).filter(Comment.post_id == post_id).count()


def get_sub_comments(db: Session, comment_id: int, start_index: int = 0, limit: int = 10):
    sub_comments_query = db.query(Comment).filter(Comment.parent_id == comment_id)

    total = sub_comments_query.count()
    total_pages = math.ceil(total / limit)

    sub_comments = sub_comments_query.offset(start_index).limit(limit).all()

    return total_pages, sub_comments


def get_best_comments(db: Session, start_index: int = 0, limit: int = 10):
    best_comments_query = db.query(Comment).join(BestComment, Comment.id == BestComment.comment_id)

    total = best_comments_query.count()
    total_pages = math.ceil(total / limit)

    best_comments = best_comments_query.offset(start_index).limit(limit).all()

    return total_pages, best_comments


def get_vocabulary_comment(db: Session, user_id: int, vocabulary_id: int):
    return db.query(Comment).filter(Comment.vocabulary_id == vocabulary_id, Comment.user_id == user_id).first()


def update_comment(db: Session, db_comment: Comment, comment_update: CommentUpdate):
    db_comment.content = comment_update.content
    db_comment.modify_date = datetime.now()
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)

    sub_comments_query = db.query(Comment).filter(Comment.parent_id == db_comment.id)
    sub_comments_count = sub_comments_query.count()
    return sub_comments_count, db_comment


def delete_comment(db: Session, db_comment: Comment):
    if db_comment.user.point >= 2:
        db_comment.user.point -= 2
    elif db_comment.user.point < 2:
        db_comment.user.point = 0

    db.delete(db_comment)
    db.commit()


BEST_COMMENT_UPDATE_CRITERIA = {
    3: 5,
    4: 7,
    5: 5,
    6: 5,
    7: 5,
    8: 5,
    9: 5,
    10: 5,
    11: 10,
    12: 6,
    13: 8,
    14: 7,
    16: 10,
    17: 10,
    18: 10,
    19: 10,
}


def update_best_comment_status(db: Session, comment_id: int):
    comment = db.query(Comment).get(comment_id)

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    best_comment = db.query(BestComment).filter(BestComment.comment_id == comment_id).first()

    if best_comment:
        return

    min_likes = BEST_COMMENT_UPDATE_CRITERIA.get(comment.post.board_id, 5)

    if comment.like_count >= min_likes:
        if not best_comment:
            best_comment = BestComment(comment_id=comment_id)
            comment.user.point += 30
            db.add(best_comment)

    db.commit()
