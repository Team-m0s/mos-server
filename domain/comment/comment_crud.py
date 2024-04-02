import math
from datetime import datetime

from sqlalchemy.orm import Session

from domain.comment.comment_schema import CommentCreate, CommentUpdate, CommentDelete, SubCommentCreate, \
    NoticeCommentCreate
from models import Post, Comment, User, Notice


def create_comment(db: Session, post: Post, comment_create: CommentCreate, user: User):
    db_comment = Comment(post=post,
                         content=comment_create.content,
                         is_anonymous=comment_create.is_anonymous,
                         create_date=datetime.now(),
                         user=user)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def create_sub_comment(db: Session, comment: Comment, sub_comment_create: SubCommentCreate, user: User):
    db_sub_comment = Comment(post=comment.post,
                             parent_id=comment.id,
                             content=sub_comment_create.content,
                             is_anonymous=sub_comment_create.is_anonymous,
                             create_date=datetime.now(),
                             user=user)
    db.add(db_sub_comment)
    db.commit()
    db.refresh(db_sub_comment)
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
    db.delete(db_comment)
    db.commit()
