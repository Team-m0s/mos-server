from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Post


def delete_blinded_posts(db: Session):
    one_week_ago = datetime.now() - timedelta(weeks=1)
    blinded_posts = db.query(Post).filter(Post.is_blinded == True, Post.blind_date <= one_week_ago).all()

    for post in blinded_posts:
        db.delete(post)

    db.commit()