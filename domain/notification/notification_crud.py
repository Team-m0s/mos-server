import math
from sqlalchemy import and_
from sqlalchemy.orm import Session
from models import User, Notification


def get_notification_list(db: Session, user: User, start_index: int = 0, limit: int = 10):
    query = db.query(Notification).filter(Notification.user_id == user.id)

    query = query.order_by(Notification.create_date.desc())

    total = query.count()
    total_pages = math.ceil(total / limit)

    my_notification_list = query.offset(start_index).limit(limit).all()

    return total_pages, my_notification_list


def get_unread_notification_count(db: Session, user: User):
    unread_notifications = db.query(Notification).filter(and_(Notification.user_id == user.id,
                                                              Notification.is_read == False)).all()
    unread_notifications_count = len(unread_notifications)

    return unread_notifications_count
