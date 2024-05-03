from sqlalchemy.orm import Session
from models import Post, Comment, Like, User, Accompany
from domain.post import post_crud
from domain.comment import comment_crud

def get_post_like(db: Session, post_id: int, user: User):
    like = db.query(Like).filter(Like.post_id == post_id, Like.user_id == user.id).first()
    return like


def get_user_like(db: Session, user: User):
    return db.query(Like).filter(Like.user_id == user.id).all()


def plus_post_like(db: Session, post: Post, user: User):
    db_like = Like(post_id=post.id,
                   user_id=user.id)
    db.add(db_like)
    post.like_count += 1
    db.commit()
    db.refresh(post)
    post_crud.update_hot_status(db, post_id=post.id)


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
    db.refresh(comment)
    comment_crud.update_best_comment_status(db, comment_id=comment.id)


def minus_comment_like(db: Session, like: Like, comment: Comment):
    db.delete(like)
    comment.like_count -= 1
    db.commit()


def get_accompany_like(db: Session, accompany_id: int, user: User):
    like = db.query(Like).filter(Like.accompany_id == accompany_id, Like.user_id == user.id).first()
    return like


def plus_accompany_like(db: Session, accompany: Accompany, user: User):
    db_like = Like(accompany_id=accompany.id,
                   user_id=user.id)
    db.add(db_like)
    accompany.like_count += 1
    db.commit()


def minus_accompany_like(db: Session, like: Like, accompany: Accompany):
    db.delete(like)
    accompany.like_count -= 1
    db.commit()
