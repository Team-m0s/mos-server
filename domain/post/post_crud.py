from datetime import datetime

from domain.post.post_schema import PostCreate, PostUpdate
from models import Post, User, Board
from sqlalchemy.orm import Session


def get_post_list(db: Session, start_index: int = 0, limit: int = 10):
    post_list = db.query(Post).order_by(Post.create_date.desc())

    total = post_list.count()
    _post_list = post_list.offset(start_index).limit(limit).all()
    return total, _post_list


def get_post(db: Session, post_id: int):
    post = db.query(Post).get(post_id)
    return post


def create_post(db: Session, post_create: PostCreate, board: Board, user: User):
    db_post = Post(board=board,
                   subject=post_create.subject,
                   content=post_create.content,
                   content_img=post_create.content_img,
                   is_anonymous=post_create.is_anonymous,
                   create_date=datetime.now(),
                   user=user)
    db.add(db_post)
    db.commit()


def update_post(db: Session, db_post: Post, post_update: PostUpdate):
    db_post.subject = post_update.subject
    db_post.content = post_update.content
    db_post.content_img = post_update.content_img
    db_post.is_anonymous = post_update.is_anonymous
    db_post.modify_date = datetime.now()
    db.add(db_post)
    db.commit()


def delete_post(db: Session, db_post: Post):
    db.delete(db_post)
    db.commit()
