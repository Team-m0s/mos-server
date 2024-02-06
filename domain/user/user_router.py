from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from database import get_db
from domain.user import user_crud, user_schema

router = APIRouter(
    prefix="/api/user",
)


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def user_create(user_info: dict, user_create_: user_schema.UserCreate, db: Session = Depends(get_db)):
    existing_user = user_crud.get_user_by_email(db, user_info['email'])
    if existing_user:
        return RedirectResponse(url="/welcome", status_code=status.HTTP_302_FOUND)
    user_crud.create_user(db, user_info=user_info, user_create=user_create_)
