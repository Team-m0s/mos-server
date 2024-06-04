from fastapi import APIRouter, Depends, HTTPException, status, Header, Form, File, UploadFile
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse
import json

from models import User
from database import get_db
from domain.user import user_crud
from domain.user.user_schema import UserUpdate, UserCreate, ImageCreate, LanguagePref, NotificationSettingUpdate
from domain.post import post_schema
from domain.post import post_crud
from domain.like import like_crud
from domain.accompany import accompany_schema
from utils import file_utils

router = APIRouter(
    prefix="/api/user",
)


def parse_lang_level(lang_level_str: str = Form(None)):
    try:
        return json.loads(lang_level_str)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid lang_level format")


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT, tags=["User"])
def user_create(user_info: dict, user_create_: UserCreate, db: Session = Depends(get_db)):
    existing_user = user_crud.get_user_by_email(db, user_info['email'])
    if existing_user:
        return RedirectResponse(url="/welcome", status_code=status.HTTP_302_FOUND)
    user_crud.create_user(db, user_info=user_info, user_create=user_create_)


@router.get("/check/nickname", status_code=status.HTTP_200_OK, tags=["User"])
def user_check_nickname(nickname: str, db: Session = Depends(get_db)):
    existing_user = user_crud.check_nickname_duplication(db, nickname=nickname)
    if existing_user:
        raise HTTPException(status_code=400, detail="This nickname is already in use.")
    return {"detail": "This nickname is available."}


@router.put("/update/profile", status_code=status.HTTP_204_NO_CONTENT, tags=["User"])
def user_profile_update(token: str = Header(), user_id: int = Form(...),
                        nickname: str = Form(...), lang_level: dict = Depends(parse_lang_level),
                        introduce: str = Form(None), profile_image: UploadFile = File(None),
                        db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")

    image_create = None
    if profile_image:
        image_hash = file_utils.calculate_image_hash(profile_image)
        existing_image = user_crud.get_image_by_hash(db, image_hash=image_hash)
        if existing_image:
            image_create = ImageCreate(image_url=existing_image.image_url, image_hash=image_hash)
        else:
            image_path = file_utils.save_image_file(profile_image)
            image_create = ImageCreate(image_url=image_path, image_hash=image_hash)

    user_update_data = UserUpdate(id=user_id, nickName=nickname, lang_level=lang_level,
                                  introduce=introduce, images_user=image_create)

    user_crud.update_user_profile(db, db_user=current_user, user_update=user_update_data)


@router.put("/update/language_preference", status_code=status.HTTP_204_NO_CONTENT, tags=["User"])
def user_language_preference_update(language_preference: LanguagePref, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)
    user_crud.update_user_language_preference(db, db_user=current_user, new_language_preference=language_preference)


@router.put("/update/notification_setting", status_code=status.HTTP_204_NO_CONTENT, tags=["User"])
def user_notification_setting_update(notification_setting: NotificationSettingUpdate, token: str = Header(),
                                     db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)
    user_crud.update_user_notification_setting(db, db_user=current_user, new_noti_setting=notification_setting)


@router.post("/findUser", tags=["User"])
def find_user(token: str = Header(), db: Session = Depends(get_db)):
    current_user_ = user_crud.get_current_user(db, token)
    return current_user_
