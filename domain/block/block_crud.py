from datetime import datetime
from sqlalchemy.orm import Session
from models import User, Block


def get_blocked_list(db: Session, user: User):
    return db.query(Block).filter(Block.blocker_uuid == user.uuid).all()


def block_user(db: Session, user: User, blocked_uuid: str):
    db_block = Block(blocker_uuid=user.uuid,
                     blocked_uuid=blocked_uuid)
    db.add(db_block)
    db.commit()
