from datetime import datetime
from sqlalchemy.orm import Session
from models import User, Block
from domain.block.block_schema import BlockUser
from domain.user import user_crud
from domain.chat import chat_crud


def get_blocked_list(db: Session, user: User):
    return db.query(Block).filter(Block.blocker_uuid == user.uuid).all()


def block_user(db: Session, user: User, blocked_user: BlockUser):
    db_block = Block(blocker_uuid=user.uuid,
                     blocked_uuid=blocked_user.blocked_uuid,
                     blocked_firebase_uuid=blocked_user.blocked_firebase_uuid)
    db.add(db_block)
    db.commit()

    # Get all personal chats the user and blocked user are participating in
    talks_ref = user_crud.firebase_db.collection('talks')
    talks = talks_ref.where('participants', 'array_contains', user.firebase_uuid).where('participants',
                                                                                        'array_contains',
                                                                                        blocked_user.blocked_firebase_uuid).get()

    # Exit the user from each personal chat with the blocked user
    for talk in talks:
        chat_crud.exit_personal_chat(talk.id, user)
