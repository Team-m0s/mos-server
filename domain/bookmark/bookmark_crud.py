import math
from datetime import datetime
from sqlalchemy.orm import Session
from models import Post, User, Bookmark, Comment


def get_bookmark_list(db: Session, user: User, start_index: int = 0, limit: int = 10):
    query = db.query(Bookmark).filter(Bookmark.user_id == user.id)

    query = query.order_by(Bookmark.create_date.desc())

    total = query.count()
    total_pages = math.ceil(total / limit)

    my_bookmark_list = query.offset(start_index).limit(limit).all()

    return total_pages, my_bookmark_list


def get_post_bookmark(db: Session, post_id: int, user: User):
    bookmark = db.query(Bookmark).filter(Bookmark.post_id == post_id, Bookmark.user_id == user.id).first()
    return bookmark


def get_bookmark_by_id(db: Session, bookmark_id: int):
    return db.query(Bookmark).get(bookmark_id)


def create_bookmark(db: Session, post: Post, user: User):
    db_bookmark = Bookmark(post=post,
                           user=user,
                           create_date=datetime.now())
    db.add(db_bookmark)
    db.commit()


def delete_bookmark(db: Session, db_bookmark: Bookmark):
    db.delete(db_bookmark)
    db.commit()
