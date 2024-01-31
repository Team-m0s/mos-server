from datetime import datetime

from sqlalchemy.orm import Session

from domain.comment.comment_schema import CommentCreate
from models import Post, Comment


def create_answer(db: Session, post: Post, comment_create: CommentCreate):
    db_comment = Comment(post=post,
                         content=comment_create.content,
                         create_date=datetime.now())
    db.add(db_comment)
    db.commit()
