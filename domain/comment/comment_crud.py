from datetime import datetime

from sqlalchemy.orm import Session

from domain.comment.comment_schema import CommentCreate
from models import Post, Comment


def create_comment(db: Session, post: Post, comment_create: CommentCreate):
    db_comment = Comment(post=post,
                         content=comment_create.content,
                         create_date=datetime.now())
    db.add(db_comment)
    db.commit()


def get_comment(db: Session, comment_id: int):
    comment = db.query(Comment).get(comment_id)
    return comment
