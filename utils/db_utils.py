from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Post, Accompany


def delete_blinded_contents():
    db = SessionLocal()
    one_week_ago = datetime.now() - timedelta(weeks=1)
    blinded_posts = db.query(Post).filter(Post.is_blinded == True, Post.blind_date <= one_week_ago).all()
    blinded_accompanies = db.query(Accompany).filter(Accompany.is_blinded == True,
                                                     Accompany.blind_date <= one_week_ago).all()

    for post in blinded_posts:
        db.delete(post)

    for accompany in blinded_accompanies:
        db.delete(accompany)

    db.commit()