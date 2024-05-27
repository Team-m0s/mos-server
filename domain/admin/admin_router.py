from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.admin import admin_crud
from domain.user import user_crud
from domain.user import user_schema
from domain.admin import admin_schema
from utils import file_utils

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


@router.get("/insights")
def insight_lists(db: Session = Depends(get_db)):
    return admin_crud.get_insights(db)


@router.post("/upload/images", status_code=status.HTTP_204_NO_CONTENT)
def upload_images(images: List[UploadFile] = File(), token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    #if not current_user.is_admin:
    #    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    image_url = []
    for image in images:
        image_path = file_utils.save_image_file(image)
        image_url.append(f"https://www.mos-server.store/static/{image_path}")

    return image_url


@router.post("/create/insight", status_code=status.HTTP_204_NO_CONTENT)
def insight_create(_insight_create: admin_schema.InsightCreate, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    admin_crud.create_insight(db, insight_create=_insight_create)
