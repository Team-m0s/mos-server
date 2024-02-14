from fastapi import APIRouter, Depends, Form, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from starlette import status

from database import get_db
from domain.accompany import accompany_schema, accompany_crud
from domain.user import user_crud
from utils import file_utils


router = APIRouter(
    prefix="/api/accompany"
)


@router.get("/list", response_model=list[accompany_schema.AccompanyBase], tags=["Accompany"])
def accompany_list(db: Session = Depends(get_db)):
    _accompany_list = accompany_crud.get_accompany_list(db)

    for accompany in _accompany_list:
        leader = user_crud.get_user_by_id(db, user_id=accompany.leader_id)
        accompany.leader = leader
        accompany.member = [member for member in accompany.member if member.id != accompany.leader_id]
    return _accompany_list


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT, tags=["Accompany"])
def accompany_create(token: str = Form(...), category: str = Form(...),
                     title: str = Form(...), activity_scope: accompany_schema.ActivityScope = Form(...),
                     images: List[UploadFile] = File(None), city: str = Form(...),
                     introduce: str = Form(...), total_member: int = Form(...),
                     tags: List[str] = Form(...), db: Session = Depends(get_db)):

    current_user = user_crud.get_current_user(db, token)

    image_path = []
    if images:
        for image in images:
            image_path.append(file_utils.save_image_file(image))

    split_tags = [tag.strip() for sublist in tags for tag in sublist.split(',')]
    image_creates = [accompany_schema.ImageCreate(image_url=path) for path in image_path]
    tag_creates = [accompany_schema.TagCreate(name=tag) for tag in split_tags]
    print(image_creates)
    print(tag_creates)

    accompany_create_data = accompany_schema.AccompanyCreate(title=title, category=category,
                                                             activity_scope=activity_scope, images_accompany=image_creates,
                                                             city=city, introduce=introduce, total_member=total_member,
                                                             tags_accompany=tag_creates)
    accompany_crud.create_accompany(db, accompany_create=accompany_create_data, user=current_user)



