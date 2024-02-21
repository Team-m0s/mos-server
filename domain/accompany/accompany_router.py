from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from starlette import status

from database import get_db
from domain.accompany import accompany_schema, accompany_crud
from domain.notice import notice_schema, notice_crud
from domain.user import user_crud
from utils import file_utils

router = APIRouter(
    prefix="/api/accompany"
)


@router.get("/list", response_model=list[accompany_schema.AccompanyBase], tags=["Accompany"])
def accompany_list(db: Session = Depends(get_db), search_keyword: str = None, sort_order: str = 'latest'):
    _accompany_list = accompany_crud.get_accompany_list(db, search_keyword=search_keyword, sort_order=sort_order)

    for accompany in _accompany_list:
        leader = user_crud.get_user_by_id(db, user_id=accompany.leader_id)
        if leader.lang_level is None:
            leader.lang_level = {}
        accompany.leader = leader
        accompany.member = [member for member in accompany.member if member.id != accompany.leader_id]

        images = accompany_crud.get_image_by_accompany_id(db, accompany_id=accompany.id)
        accompany.image_urls = [accompany_schema.ImageBase(id=image.id,
                                                           image_url=f"https://www.mos-server.store/static/{image.image_url}")
                                for
                                image in images if image.image_url] if images else []
    return _accompany_list


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT, tags=["Accompany"])
def accompany_create(token: str = Header(), category: accompany_schema.Category = Form(...),
                     title: str = Form(...), activity_scope: accompany_schema.ActivityScope = Form(...),
                     images: List[UploadFile] = File(None), city: str = Form(None),
                     introduce: str = Form(...), total_member: int = Form(...),
                     tags: List[str] = Form(None), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    image_creates = []
    if images:
        for image in images:
            image_hash = file_utils.calculate_image_hash(image)
            existing_image = accompany_crud.get_image_by_hash(db, image_hash)
            if existing_image:
                image_creates.append(
                    accompany_schema.ImageCreate(image_url=existing_image.image_url, image_hash=image_hash))
            else:
                image_path = file_utils.save_image_file(image)
                image_creates.append(accompany_schema.ImageCreate(image_url=image_path, image_hash=image_hash))

    split_tags = []
    if tags and any(tags):
        split_tags = [tag.strip() for sublist in tags for tag in sublist.split(',')]

    tag_creates = [accompany_schema.TagCreate(name=tag) for tag in split_tags]

    accompany_create_data = accompany_schema.AccompanyCreate(title=title, category=category,
                                                             activity_scope=activity_scope,
                                                             images_accompany=image_creates,
                                                             city=city, introduce=introduce, total_member=total_member,
                                                             tags_accompany=tag_creates)
    accompany_crud.create_accompany(db, accompany_create=accompany_create_data, user=current_user)


@router.post("/create/notice", status_code=status.HTTP_204_NO_CONTENT, tags=["Accompany"])
def accompany_create_notice(accompany_id: int, _notice_create: notice_schema.NoticeCreate, token: str = Header(),
                            db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    accompany = accompany_crud.get_accompany_by_id(db, accompany_id=accompany_id)
    if not accompany:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"동행을 찾을 수 없습니다.")

    if current_user.id != accompany.leader_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")

    notice_crud.create_accompany_notice(db, accompany_id=accompany_id, notice_create=_notice_create)


@router.put("/update/notice", status_code=status.HTTP_204_NO_CONTENT, tags=["Accompany"])
def accompany_update_notice(_notice_update: notice_schema.NoticeUpdate, token: str = Header(),
                            db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    notice = notice_crud.get_notice_by_id(db, notice_id=_notice_update.notice_id)
    if not notice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"데이터를 찾을 수 없습니다.")

    accompany = accompany_crud.get_accompany_by_id(db, accompany_id=notice.accompany_id)
    if current_user.id != accompany.leader_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")

    notice_crud.update_accompany_notice(db, db_notice=notice, notice_update=_notice_update)


@router.delete("/delete/notice", status_code=status.HTTP_204_NO_CONTENT, tags=["Accompany"])
def accompany_delete_notice(_notice_delete: notice_schema.NoticeDelete, token: str = Header(),
                            db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    notice = notice_crud.get_notice_by_id(db, notice_id=_notice_delete.notice_id)
    if not notice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"데이터를 찾을 수 없습니다.")

    accompany = accompany_crud.get_accompany_by_id(db, accompany_id=notice.accompany_id)
    if current_user.id != accompany.leader_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")

    notice_crud.delete_accompany_notice(db, db_notice=notice)


@router.delete("/ban-member/{accompany_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Accompany"])
def accompany_ban_member(accompany_id: int, user_id: int, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    accompany = accompany_crud.get_accompany_by_id(db, accompany_id=accompany_id)
    if not accompany:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"동행을 찾을 수 없습니다.")

    if current_user.id != accompany.leader_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")

    member = user_crud.get_user_by_id(db, user_id=user_id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"해당 멤버가 존재하지 않습니다.")

    accompany_crud.ban_accompany_member(db, accompany_id=accompany.id, member_id=member.id)


@router.put("/delegate-leader/{accompany_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Accompany"])
def accompany_delegate_leader(accompany_id: int, user_id: int, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    accompany = accompany_crud.get_accompany_by_id(db, accompany_id=accompany_id)
    if not accompany:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"동행을 찾을 수 없습니다.")

    if current_user.id != accompany.leader_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")

    member = user_crud.get_user_by_id(db, user_id=user_id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"해당 멤버가 존재하지 않습니다.")

    accompany_crud.assign_new_leader(db, accompany_id=accompany_id, member_id=member.id)

