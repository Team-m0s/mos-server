from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.admin import admin_crud
from domain.user import user_crud
from domain.user import user_schema

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
)


@router.get("/user/lists", response_model=user_schema.UserListResponse)
def user_list(token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    total_users, users = admin_crud.get_all_users(db)
    return {"total_users": total_users, "users": users}
