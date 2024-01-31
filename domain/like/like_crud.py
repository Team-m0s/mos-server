from datetime import datetime

from sqlalchemy.orm import Session

from models import Post, Comment, Like


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
