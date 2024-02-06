from datetime import datetime

from domain.post.post_schema import PostCreate
from models import Post
from sqlalchemy.orm import Session


def get_post_list(db: Session):
    post_list = db.query(Post).order_by(Post.create_date.desc()).all()
    return post_list


def get_post(db: Session, post_id: int):
    post = db.query(Post).get(post_id)
    return post


def create_post(db: Session, post_create: PostCreate):
    db_post = Post(subject=post_create.subject,
                   content=post_create.content,
                   create_date=datetime.now())
    db.add(db_post)
    db.commit()
