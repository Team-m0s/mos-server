from sqlalchemy.orm import Session
from datetime import datetime

from domain.notice.notice_schema import NoticeCreate, NoticeUpdate
from domain.accompany import accompany_crud
from models import Notice


def get_notice_by_id(db: Session, notice_id: int):
    return db.query(Notice).filter(Notice.id == notice_id).first()


def create_accompany_notice(db: Session, accompany_id: int, notice_create: NoticeCreate):
    db_accompany = accompany_crud.get_accompany_by_id(db, accompany_id=accompany_id)
    db_accompany.update_date = datetime.now()
    db.add(db_accompany)

    db_notice = Notice(content=notice_create.content,
                       create_date=datetime.now(),
                       accompany_id=accompany_id)
    db.add(db_notice)
    db.commit()


def update_accompany_notice(db: Session, db_notice: Notice, notice_update: NoticeUpdate):
    db_notice.content = notice_update.content
    db_notice.update_date = datetime.now()
    db.add(db_notice)
    db.commit()


def delete_accompany_notice(db: Session, db_notice: Notice):
    db.delete(db_notice)
    db.commit()
