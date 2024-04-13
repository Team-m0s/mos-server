from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.notification import notification_schema
from domain.notification import notification_crud
from domain.user import user_crud

router = APIRouter(
    prefix="/api/notification",
)


@router.get("/list", response_model=list[notification_schema.Notification], tags=["Notification"])
def notification_list(token: str = Header(), db: Session = Depends(get_db), page: int = 0, size: int = 10):
    current_user = user_crud.get_current_user(db, token)
    total_pages, _my_notification_list = notification_crud.get_notification_list(db, user=current_user,
                                                                                 start_index=page * size, limit=size)

    for notification in _my_notification_list:
        notification.total_pages = total_pages

    return _my_notification_list
