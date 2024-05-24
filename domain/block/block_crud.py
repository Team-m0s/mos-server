from datetime import datetime
from sqlalchemy.orm import Session
from models import User, Block
from domain.block.block_schema import BlockUser
from domain.user import user_crud
from domain.chat import chat_crud


def get_blocked_list(db: Session, user: User):
    return db.query(Block).filter(Block.blocker_uuid == user.uuid).all()


def is_user_blocked(db: Session, user: User, blocked_user: User):
    db_blocked = db.query(Block).filter(Block.blocker_uuid == user.uuid) & \
                 ((Block.blocked_uuid == blocked_user.uuid) |
                  (Block.blocked_firebase_uuid == blocked_user.firebase_uuid)).first()
    return db_blocked


def block_user(db: Session, user: User, blocked_user: BlockUser):
    db_block = Block(blocker_uuid=user.uuid,
                     blocked_uuid=blocked_user.blocked_uuid,
                     blocked_firebase_uuid=blocked_user.blocked_firebase_uuid)
    db.add(db_block)
    db.commit()

    # Get all personal chats the user is participating in
    talks_ref = user_crud.firebase_db.collection('talks')
    user_talks = talks_ref.where('participants', 'array_contains', user.firebase_uuid).get()

    # Get all personal chats the blocked user is participating in
    blocked_user_talks = talks_ref.where('participants', 'array_contains', blocked_user.blocked_firebase_uuid).get()

    # 사용자가 참여 중인 대화 ID 집합 생성
    user_talk_ids = {talk.id for talk in user_talks}
    # 차단된 사용자가 참여 중인 대화 ID 집합 생성
    blocked_user_talk_ids = {talk.id for talk in blocked_user_talks}

    # 공통 대화 찾기
    common_talk_ids = user_talk_ids.intersection(blocked_user_talk_ids)

    # Exit the user from each personal chat with the blocked user
    for talk_id in common_talk_ids:
        chat_crud.exit_personal_chat(talk_id, user)
