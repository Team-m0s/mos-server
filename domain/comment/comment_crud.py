from datetime import datetime

from sqlalchemy.orm import Session

from domain.comment.comment_schema import CommentCreate, CommentUpdate, CommentDelete, SubCommentCreate, NoticeCommentCreate
from models import Post, Comment, User, Notice


def create_comment(db: Session, post: Post, comment_create: CommentCreate, user: User):
    db_comment = Comment(post=post,
                         content=comment_create.content,
                         is_anonymous=comment_create.is_anonymous,
                         create_date=datetime.now(),
                         user=user)
    db.add(db_comment)
    db.commit()


def create_sub_comment(db: Session, comment: Comment, sub_comment_create: SubCommentCreate, user: User):
    db_sub_comment = Comment(post=comment.post,
                             parent_id=comment.id,
                             content=sub_comment_create.content,
                             is_anonymous=sub_comment_create.is_anonymous,
                             create_date=datetime.now(),
                             user=user)
    db.add(db_sub_comment)
    db.commit()


def create_notice_comment(db: Session, notice: Notice, notice_comment_create: NoticeCommentCreate, user: User):
    db_notice_comment = Comment(notice=notice,
                                content=notice_comment_create.content,
                                is_anonymous=False,
                                create_date=datetime.now(),
                                user=user)
    db.add(db_notice_comment)
    db.commit()


def get_comment(db: Session, comment_id: int):
    comment = db.query(Comment).get(comment_id)
    return comment


def update_comment(db: Session, db_comment: Comment, comment_update: CommentUpdate):
    db_comment.content = comment_update.content
    db_comment.modify_date = datetime.now()
    db.add(db_comment)
    db.commit()


def delete_comment(db: Session, db_comment: Comment):
    db.delete(db_comment)
    db.commit()
