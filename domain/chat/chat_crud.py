from datetime import datetime
from sqlalchemy.orm import Session
from models import User, Accompany

from google.cloud import firestore
from domain.user import user_crud
import hashlib


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
    participants = [sender.firebase_uuid, receiver.firebase_uuid]

    sorted_uuids = ''.join(sorted(participants))

    hash_object = hashlib.sha256(sorted_uuids.encode())
    hex_dig = hash_object.hexdigest()

    talk_content = {
        "lastMessage": message,
        "sendTime": datetime.utcnow(),
        "participants": participants,
        "chatName": receiver.nickName
    }

    talk_ref = user_crud.firebase_db.collection('talks').document(hex_dig)
    talk_ref.update(talk_content)

    message_content = {
        "text": message,
        "sender_uid": sender.firebase_uuid,
        "sender_profile_img": sender.profile_img,
        "sender_nickname": sender.nickName,
        "sendTime": datetime.utcnow()
    }

    message_ref = user_crud.firebase_db.collection('talks').document(hex_dig).collection('messages')
    message_ref.add(message_content)
