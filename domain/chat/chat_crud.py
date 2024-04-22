from datetime import datetime
from sqlalchemy.orm import Session
from models import User, Accompany

from google.cloud import firestore
from domain.user import user_crud
from models import Notification
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
        "firebase_uuid": user.firebase_uuid,
        "reportCount": 0,
        "isBlinded": False
    }

    chat_ref = user_crud.firebase_db.collection('chats').document(str(accompany.id)).collection('messages')
    chat_ref.add(message_content)


def create_personal_chat(db: Session, sender: User, receiver: User, message: str, is_anonymous: bool):
    participants = [sender.firebase_uuid, receiver.firebase_uuid]

    sorted_uuids = ''.join(sorted(participants))

    hash_object = hashlib.sha256(sorted_uuids.encode())
    hex_dig = hash_object.hexdigest()

    talk_content = {
        "talkID": hex_dig,
        "lastMessage": message,
        "lastMessageTime": datetime.utcnow(),
        "participants": participants,
        "isAnonymous": is_anonymous
    }

    talk_ref = user_crud.firebase_db.collection('talks').document(hex_dig)
    talk_ref.set(talk_content, merge=True)

    message_content = {
        "text": message,
        "firebase_uuid": sender.firebase_uuid,
        "profileImg": sender.profile_img,
        "nickName": sender.nickName,
        "sendTime": datetime.utcnow(),
        "reportCount": 0,
        "isBlinded": False
    }

    message_ref = user_crud.firebase_db.collection('talks').document(hex_dig).collection('messages')
    message_ref.add(message_content)

    db_notification = Notification(title=f'"{receiver.nickName}"님으로부터 새로운 메시지가 있어요!',
                                   body=message,
                                   sender_firebase_uuid=sender.firebase_uuid,
                                   create_date=datetime.now(),
                                   is_Post=False,
                                   user_id=receiver.id)

    db.add(db_notification)
    db.commit()


def exit_personal_chat(talk_id: str, user: User):
    chat_ref = user_crud.firebase_db.collection('talks').document(talk_id)
    chat = chat_ref.get()
    if chat.exists:
        participants = chat.get('participants')
        if user.firebase_uuid in participants:
            participants.remove(user.firebase_uuid)
            if len(participants) == 0:
                chat_ref.delete()
            else:
                chat_ref.update({"participants": participants})
        else:
            raise Exception("User not found in chat participants")
    else:
        raise Exception("Chat not found")
