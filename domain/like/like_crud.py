from datetime import datetime

from sqlalchemy.orm import Session

from models import Post, Comment, Like, User


def post_like(db: Session, post: Post):
    db_like = Like(post=post)
    db.add(db_like)
    post.like_count += 1
    db.commit()


def comment_like(db: Session, comment: Comment):
    db_like = Like(comment=comment)
    db.add(db_like)
    comment.like_count += 1
    db.commit()


def get_post_like(db: Session, post_id: int, user: User):
    like = db.query(Like).filter(Like.post_id == post_id, Like.user_id == user.id).first()
    return like


def plus_post_like(db: Session, post: Post, user: User):
    db_like = Like(post_id=post.id,
                   user_id=user.id)
    db.add(db_like)
    post.like_count += 1
    db.commit()


def minus_post_like(db: Session, like: Like, post: Post):
    db.delete(like)
    post.like_count -= 1
    db.commit()


def get_comment_like(db: Session, comment_id: int, user: User):
    like = db.query(Like).filter(Like.comment_id == comment_id, Like.user_id == user.id).first()
    return like


def plus_comment_like(db: Session, comment: Comment, user: User):
    db_like = Like(comment_id=comment.id,
                   user_id=user.id)
    db.add(db_like)
    comment.like_count += 1
    db.commit()


def minus_comment_like(db: Session, like: Like, comment: Comment):
    db.delete(like)
    comment.like_count -= 1
    db.commit()
