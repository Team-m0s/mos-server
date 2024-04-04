from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from starlette import status
from datetime import datetime

from database import get_db
from domain.user import user_crud
from domain.accompany import accompany_crud
from domain.chat import chat_crud
from domain.chat import chat_schema

router = APIRouter(
    prefix="/api/chat",
)


@router.post("/accompany/create", status_code=status.HTTP_204_NO_CONTENT, tags=["Chat"])
def accompany_chat_create(accompany_id: int, message: str, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    if current_user.suspension_period and current_user.suspension_period > datetime.now():
        raise HTTPException(status_code=403, detail="User is currently suspended")

    db_accompany = accompany_crud.get_accompany_by_id(db, accompany_id=accompany_id)

    if not db_accompany:
        raise HTTPException(status_code=404, detail="Accompany not found")

    chat_crud.create_accompany_chat(accompany=db_accompany, user=current_user, message=message)


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

    chat_crud.create_personal_chat(sender=sender, receiver=receiver, message=personal_chat.message)
