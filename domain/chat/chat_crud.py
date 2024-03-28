from datetime import datetime
from sqlalchemy.orm import Session
from models import User, Accompany

from domain.user import user_crud


def create_accompany_chat(accompany: Accompany, user: User, message: str):
    if accompany.leader_id == user.id:
        is_leader = True
    else:
        is_leader = False

    message_content = {
        "isLeader": is_leader,
        "sendTime": datetime.now(),
        "text": message,
        "userUid": user.firebase_uuid
    }

    doc_ref = user_crud.firebase_db.collection('chats').document(accompany.id)
    doc_ref.set({
        "message": message_content
    })
