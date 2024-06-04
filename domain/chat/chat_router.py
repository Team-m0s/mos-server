from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from starlette import status
from datetime import datetime

from database import get_db
from firebase_admin import messaging
from domain.user import user_crud
from domain.accompany import accompany_crud
from domain.chat import chat_crud
from domain.chat import chat_schema
from domain.notification import notification_crud
from domain.block import block_crud

router = APIRouter(
    prefix="/api/chat",
)


@router.post("/accompany/create", status_code=status.HTTP_204_NO_CONTENT, tags=["Chat"])
def accompany_chat_create(accompany_chat: chat_schema.AccompanyChat, token: str = Header(),
                          db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    if current_user.suspension_period and current_user.suspension_period > datetime.now():
        raise HTTPException(status_code=403, detail="User is currently suspended")

    db_accompany = accompany_crud.get_accompany_by_id(db, accompany_id=accompany_chat.accompany_id)

    if not db_accompany:
        raise HTTPException(status_code=404, detail="Accompany not found")

    chat_crud.create_accompany_chat(accompany=db_accompany, user=current_user, message=accompany_chat.message)


@router.post("/personal/create", status_code=status.HTTP_204_NO_CONTENT, tags=["Chat"])
def personal_chat_create(personal_chat: chat_schema.PersonalChat, token: str = Header(), db: Session = Depends(get_db)):
    sender = user_crud.get_current_user(db, token)

    if sender.suspension_period and sender.suspension_period > datetime.now():
        raise HTTPException(status_code=403, detail="User is currently suspended")

    if sender.firebase_uuid != personal_chat.sender_id:
        raise HTTPException(status_code=404, detail="Can not match user")

    receiver = user_crud.get_user_by_firebase_uuid(db, uuid=personal_chat.receiver_id)

    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    talk_id = chat_crud.create_personal_chat(sender=sender, receiver=receiver, message=personal_chat.message,
                                             is_anonymous=personal_chat.is_anonymous)

    badge_count = notification_crud.get_unread_notification_count(db, user=receiver)

    blocked_users = block_crud.get_blocked_list(db, user=receiver)
    blocked_uuids = {block.blocked_uuid for block in blocked_users}
    blocked_firebase_uuids = {block.blocked_firebase_uuid for block in blocked_users}

    title = chat_crud.get_chat_message_title(language_preference=receiver.language_preference,
                                             message_type='personal_chat')

    notification_setting = user_crud.get_user_notification_setting(db, receiver)

    # sender의 UUID와 firebase_uuid가 각각의 집합에 포함되어 있는지 확인
    if notification_setting.noti_chat:
        if sender.uuid not in blocked_uuids and sender.firebase_uuid not in blocked_firebase_uuids:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=personal_chat.message,
                ),
                data={
                    "talk_id": str(talk_id),
                    "last_message": str(personal_chat.message)
                },
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            badge=badge_count,
                            sound='default',
                            content_available=True,
                        )
                    )
                ),
                token=receiver.fcm_token
            )

            messaging.send(message)


@router.delete("/personal/exit", status_code=status.HTTP_204_NO_CONTENT, tags=["Chat"])
def personal_chat_exit(talk_id: str, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)
    chat_crud.exit_personal_chat(talk_id=talk_id, user=current_user)
