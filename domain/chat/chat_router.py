from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.user import user_crud
from domain.accompany import accompany_crud
from domain.chat import chat_crud

router = APIRouter(
    prefix="/api/chat",
)


@router.post("/accompany/create", status_code=status.HTTP_204_NO_CONTENT, tags=["Chat"])
def accompany_chat_create(accompany_id: int, message: str, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)
    db_accompany = accompany_crud.get_accompany_by_id(db, accompany_id=accompany_id)

    chat_crud.create_accompany_chat(accompany=db_accompany, user=current_user, message=message)
