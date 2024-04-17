from datetime import datetime
from sqlalchemy.orm import Session
from models import User, Block
from domain.block.block_schema import BlockUser


def get_blocked_list(db: Session, user: User):
    return db.query(Block).filter(Block.blocker_uuid == user.uuid).all()


def block_user(db: Session, user: User, blocked_user: BlockUser):
    db_block = Block(blocker_uuid=user.uuid,
                     blocked_uuid=blocked_user.blocked_uuid,
                     blocked_firebase_uuid=blocked_user.blocked_firebase_uuid)
    db.add(db_block)
    db.commit()
