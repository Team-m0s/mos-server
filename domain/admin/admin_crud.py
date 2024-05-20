from sqlalchemy.orm import Session
from models import User


def get_all_users(db: Session):
    db_users = db.query(User).all()
    total_users = len(db_users)

    return total_users, db_users