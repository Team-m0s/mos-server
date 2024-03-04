from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from starlette import status

from database import get_db
from domain.accompany import accompany_schema, accompany_crud
from domain.notice import notice_schema, notice_crud
from domain.user import user_crud
from domain.like import like_crud
from utils import file_utils
from models import ActivityScope, Category

router = APIRouter(
    prefix="/api/accompany"
)


def member_query_processor(total_member_min: int, total_member_max: int):
    result = [total_member_min, total_member_max]
    return result


def category_query_processor(category1: Category = None, category2: Category = None, category3: Category = None):
    if category1 is None and category2 is None and category3 is None:
        return None

    result = [category1, category2, category3]
    return result


@router.get("/list", response_model=list[accompany_schema.AccompanyBase], tags=["Accompany"])
def accompany_list(token: Optional[str] = Header(None), db: Session = Depends(get_db),
                   search_keyword: str = None, sort_order: str = 'latest'):
    current_user = None
    if token:
        current_user = user_crud.get_current_user(db, token)
    _accompany_list = accompany_crud.get_accompany_list(db, search_keyword=search_keyword, sort_order=sort_order)

    for accompany in _accompany_list:
        leader = user_crud.get_user_by_id(db, user_id=accompany.leader_id)
        if leader.lang_level is None:
            leader.lang_level = {}
        accompany.leader = leader
        accompany.member = [member for member in accompany.member if member.id != accompany.leader_id]
        for member in accompany.member:
            if member.lang_level is None:
                member.lang_level = {}

        images = accompany_crud.get_image_by_accompany_id(db, accompany_id=accompany.id)
        accompany.image_urls = [accompany_schema.ImageBase(id=image.id,
                                                           image_url=f"https://www.mos-server.store/static/{image.image_url}")
                                for
                                image in images if image.image_url] if images else []

    if current_user:
        for accompany in _accompany_list:
            accompany_like = like_crud.get_accompany_like(db, accompany_id=accompany.id, user=current_user)
            if accompany_like:
                accompany.is_like_by_user = True

    return _accompany_list


@router.get("/filtered/list", response_model=list[accompany_schema.AccompanyBase], tags=["Accompany"])
def accompany_filtered_list(is_closed: bool, total_member: List[int] = Depends(member_query_processor),
                            token: Optional[str] = Header(None), db: Session = Depends(get_db),
                            activity_scope: ActivityScope = None, city: str = None,
                            category: List[Category] = Depends(category_query_processor)):
    current_user = None
    if token:
        current_user = user_crud.get_current_user(db, token)
    _accompany_list = accompany_crud.get_accompany_filtered_list(db, is_closed=is_closed, total_member=total_member,
                                                                 activity_scope=activity_scope, city=city,
                                                                 category=category)

    for accompany in _accompany_list:
        leader = user_crud.get_user_by_id(db, user_id=accompany.leader_id)
        if leader.lang_level is None:
            leader.lang_level = {}
        accompany.leader = leader
        accompany.member = [member for member in accompany.member if member.id != accompany.leader_id]
        for member in accompany.member:
            if member.lang_level is None:
                member.lang_level = {}

        images = accompany_crud.get_image_by_accompany_id(db, accompany_id=accompany.id)
        accompany.image_urls = [accompany_schema.ImageBase(id=image.id,
                                                           image_url=f"https://www.mos-server.store/static/{image.image_url}")
                                for
                                image in images if image.image_url] if images else []

    if current_user:
        for accompany in _accompany_list:
            accompany_like = like_crud.get_accompany_like(db, accompany_id=accompany.id, user=current_user)
            if accompany_like:
                accompany.is_like_by_user = True

    return _accompany_list


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT, tags=["Accompany"])
def accompany_create(token: str = Header(), category: accompany_schema.Category = Form(...),
                     title: str = Form(...), activity_scope: accompany_schema.ActivityScope = Form(...),
                     images: List[UploadFile] = File(None), city: str = Form(None),
                     introduce: str = Form(...), total_member: int = Form(...),
                     tags: List[str] = Form(None), qna: str = Form(None), db: Session = Depends(get_db)):
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
                                                             tags_accompany=tag_creates, qna=qna)
    accompany_crud.create_accompany(db, accompany_create=accompany_create_data, user=current_user)


@router.put("/update", status_code=status.HTTP_204_NO_CONTENT, tags=["Accompany"])
def accompany_update(token: str = Header(), accompany_id: int = Form(...),
                     category: accompany_schema.Category = Form(...),
                     title: str = Form(...), activity_scope: accompany_schema.ActivityScope = Form(...),
                     images: List[UploadFile] = File(None), city: str = Form(None),
                     introduce: str = Form(...), total_member: int = Form(...),
                     tags: List[str] = Form(None), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)
    accompany = accompany_crud.get_accompany_by_id(db, accompany_id=accompany_id)
    if not accompany:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을수 없습니다.")
    if accompany.leader_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")

    image_creates = []
    if images:
        for image in images:
            image_hash = file_utils.calculate_image_hash(image)
            existing_image = accompany_crud.get_image_by_hash(db, image_hash)
            # 기존에 저장된 이미지와 hash 비교, 이미 존재하는 이미지면 다시 저장 X
            if existing_image:
                image_creates.append(
                    accompany_schema.ImageCreate(image_url=existing_image.image_url, image_hash=image_hash))
            else:
                image_path = file_utils.save_image_file(image)
                image_creates.append(accompany_schema.ImageCreate(image_url=image_path, image_hash=image_hash))

    tag_creates = []
    if tags and any(tags):
        split_tags = [tag.strip() for sublist in tags for tag in sublist.split(',')]
        tag_creates = [accompany_schema.TagCreate(name=tag) for tag in split_tags]

    accompany_update_data = accompany_schema.AccompanyUpdate(category=category, title=title,
                                                             activity_scope=activity_scope,
                                                             images_accompany=image_creates,
                                                             city=city, introduce=introduce, total_member=total_member,
                                                             tags_accompany=tag_creates, accompany_id=accompany_id)

    accompany_crud.update_accompany(db, db_accompany=accompany, accompany_update=accompany_update_data)


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


@router.get("/application/list/{accompany_id}", response_model=List[accompany_schema.ApplicationBase],
            tags=["Accompany"])
def accompany_application_list(accompany_id: int, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)
    accompany = accompany_crud.get_accompany_by_id(db, accompany_id=accompany_id)
    if not accompany:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Accompany not found.")
    if current_user.id != accompany.leader_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the leader can view applications.")
    return accompany_crud.get_application_list(db, accompany_id=accompany_id)


@router.post("/apply/{accompany_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Accompany"])
def accompany_apply(application_create: accompany_schema.ApplicationCreate, token: str = Header(),
                    db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)
    accompany = accompany_crud.get_accompany_by_id(db, accompany_id=application_create.accompany_id)
    if not accompany:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Accompany not found.")

    if application_create.answer is None:
        if accompany.qna:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Answer should be required.")
        accompany_crud.register_accompany(db, accompany_id=accompany.id, user_id=current_user.id)
    else:
        if accompany.qna is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Answer do not needed.")
        accompany_crud.apply_accompany(db, accompany_id=accompany.id,
                                       user_id=current_user.id, answer=application_create.answer)


@router.put("/application/approve/{application_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Accompany"])
def application_approve(application_id: int, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)
    application = accompany_crud.get_application_by_id(db, application_id=application_id)
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Application not found.")
    if current_user.id != application.accompany.leader_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the leader can approve applications.")
    accompany_crud.approve_application(db, application_id=application_id)


@router.put("/application/reject/{application_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Accompany"])
def application_reject(application_id: int, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)
    application = accompany_crud.get_application_by_id(db, application_id=application_id)
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Application not found.")
    if current_user.id != application.accompany.leader_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the leader can approve applications.")
    accompany_crud.reject_application(db, application_id=application_id)


@router.delete("/leave/{accompany_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Accompany"])
def accompany_leave(accompany_id: int, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)
    accompany = accompany_crud.get_accompany_by_id(db, accompany_id=accompany_id)
    if not accompany:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"동행을 찾을 수 없습니다.")

    if current_user.id == accompany.leader_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="리더는 동행을 탈퇴할 수 없습니다.")

    members = accompany_crud.get_members_by_accompany_id(db, accompany_id=accompany_id)
    if current_user not in members:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")

    accompany_crud.leave_accompany(db, accompany_id=accompany_id, member_id=current_user.id)


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
