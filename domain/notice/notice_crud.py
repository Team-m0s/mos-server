from sqlalchemy.orm import Session
from datetime import datetime

from domain.notice.notice_schema import NoticeCreate, NoticeBase
from models import Notice


def create_accompany_notice(db: Session, accompany_id: int, notice_create: NoticeCreate):
    db_notice = Notice(content=notice_create.content,
                       create_date=datetime.now(),
                       accompany_id=accompany_id)
    db.add(db_notice)
    db.commit()
