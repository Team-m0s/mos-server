from datetime import datetime
from sqlalchemy.orm import Session
from models import User, Accompany

from google.cloud import firestore
from domain.user import user_crud


def create_accompany_chat(accompany: Accompany, user: User, message: str):
    if accompany.leader_id == user.id:
        is_leader = True
    else:
        is_leader = False

    message_content = {
        "isLeader": is_leader,
        "sendTime": datetime.utcnow(),
        "text": message,
        "userUid": user.firebase_uuid
    }

    chat_ref = user_crud.firebase_db.collection('chats').document(str(accompany.id)).collection('messages')
    chat_ref.add(message_content)


def create_personal_chat(sender: User, receiver: User, message: str):
    message_content = {

    }
