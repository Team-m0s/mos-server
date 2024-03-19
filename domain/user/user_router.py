from fastapi import APIRouter, Depends, HTTPException, status, Header, Form, File, UploadFile
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from models import User
from database import get_db
from domain.user import user_crud
from domain.user.user_schema import UserUpdate, UserCreate, ImageCreate
from domain.post import post_schema
from domain.post import post_crud
from domain.like import like_crud
from domain.accompany import accompany_schema
from utils import file_utils

router = APIRouter(
    prefix="/api/user",
)


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT, tags=["User"])
def user_create(user_info: dict, user_create_: UserCreate, db: Session = Depends(get_db)):
    existing_user = user_crud.get_user_by_email(db, user_info['email'])
    if existing_user:
        return RedirectResponse(url="/welcome", status_code=status.HTTP_302_FOUND)
    user_crud.create_user(db, user_info=user_info, user_create=user_create_)


@router.get("/my/post/list", response_model=list[post_schema.Post], tags=["User"])
def my_post_list(token: str = Header(), db: Session = Depends(get_db), page: int = 0, size: int = 10):
    current_user = user_crud.get_current_user(db, token)
    total_pages, _my_post_list = user_crud.get_my_post_list(db, user=current_user, start_index=page * size, limit=size)

    for post in _my_post_list:
        images = post_crud.get_image_by_post_id(db, post_id=post.id)
        post.image_urls = [accompany_schema.ImageBase(id=image.id,
                                                      image_url=f"https://www.mos-server.store/static/{image.image_url}")
                           for
                           image in images if image.image_url] if images else []

        post_like = like_crud.get_post_like(db, post_id=post.id, user=current_user)
        if post_like:
            post.is_liked_by_user = True
        post.total_pages = total_pages

    return _my_post_list


@router.put("/update/profile", status_code=status.HTTP_204_NO_CONTENT, tags=["User"])
def user_profile_update(token: str = Header(), user_id: int = Form(...),
                        nickname: str = Form(...), lang_level: dict = Form(None),
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


@router.post("/findUser", tags=["User"])
def find_user(token: str = Header(), db: Session = Depends(get_db)):
    current_user_ = user_crud.get_current_user(db, token)
    return current_user_
