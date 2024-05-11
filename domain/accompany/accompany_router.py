import math

from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from starlette import status

from database import get_db
from firebase_admin import messaging
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
def accompany_list(is_closed: bool, token: Optional[str] = Header(None), db: Session = Depends(get_db),
                   page: int = 0, size: int = 10, search_keyword: str = None,
                   category: Category = None, sort_order: str = 'latest'):
    current_user = None
    if token:
        current_user = user_crud.get_current_user(db, token)
    total_pages, _accompany_list = accompany_crud.get_accompany_list(db, is_closed=is_closed, start_index=page * size,
                                                                     limit=size, search_keyword=search_keyword,
                                                                     category=category, sort_order=sort_order)

    _accompany_list = accompany_crud.set_accompany_detail(db, _accompany_list)

    if current_user:
        for accompany in _accompany_list:
            accompany_like = like_crud.get_accompany_like(db, accompany_id=accompany.id, user=current_user)
            if accompany_like:
                accompany.is_like_by_user = True

    for accompany in _accompany_list:
        accompany.total_pages = total_pages

    return _accompany_list


@router.get("/detail/{accompany_id}", response_model=accompany_schema.AccompanyBase, tags=["Accompany"])
def accompany_detail(accompany_id: int, token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    current_user = None
    if token:
        current_user = user_crud.get_current_user(db, token)
    _accompany = accompany_crud.get_accompany_detail(db, accompany_id=accompany_id)
    _accompany = accompany_crud.set_accompany_detail(db, [_accompany])[0]

    if current_user:
        accompany_like = like_crud.get_accompany_like(db, accompany_id=_accompany.id, user=current_user)
        if accompany_like:
            _accompany.is_like_by_user = True

    return _accompany


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

    _accompany_list = accompany_crud.set_accompany_detail(db, _accompany_list)

    if current_user:
        for accompany in _accompany_list:
            accompany_like = like_crud.get_accompany_like(db, accompany_id=accompany.id, user=current_user)
            if accompany_like:
                accompany.is_like_by_user = True

    return _accompany_list


@router.get("/liked/list", response_model=list[accompany_schema.AccompanyBase], tags=["Accompany"])
def get_liked_accompanies(token: str = Header(), page: int = 0, size: int = 10, db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)
    total_pages, liked_accompanies = accompany_crud.get_accompany_liked_list(db, user=current_user,
                                                                            start_index=page * size, limit=size)

    liked_accompanies = accompany_crud.set_accompany_detail(db, liked_accompanies)

    for accompany in liked_accompanies:
        accompany.total_pages = total_pages

    return liked_accompanies


@router.get("/my/list", response_model=List[accompany_schema.AccompanyBase], tags=["Accompany"])
def get_accompanies_by_user(token: str = Header(), page: int = 0, size: int = 10, db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)
    total_pages, accompanies = accompany_crud.get_accompanies_by_user_id(db, user_id=current_user.id,
                                                                         start_index=page * size, limit=size)

    accompanies = accompany_crud.set_accompany_detail(db, accompanies)

    for accompany in accompanies:
        accompany.total_pages = total_pages
    return accompanies


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT, tags=["Accompany"])
def accompany_create(token: str = Header(), category: accompany_schema.Category = Form(...),
                     title: str = Form(...), activity_scope: accompany_schema.ActivityScope = Form(...),
                     images: List[UploadFile] = File(None), city: str = Form(None),
                     introduce: str = Form(...), total_member: int = Form(...),
                     tags: List[str] = Form(None), qna: str = Form(None), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    if current_user.suspension_period and current_user.suspension_period > datetime.now():
        raise HTTPException(status_code=403, detail="User is currently suspended")

    image_creates = []
    image_hashes = set()
    if images:
        for image in images:
            image_hash = file_utils.calculate_image_hash(image)
            if image_hash in image_hashes:
                continue  # 이미 처리된 이미지 해시라면 스킵
            image_hashes.add(image_hash)

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
                     tags: List[str] = Form(None), qna: str = Form(None), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    if current_user.suspension_period and current_user.suspension_period > datetime.now():
        raise HTTPException(status_code=403, detail="User is currently suspended")

    accompany = accompany_crud.get_accompany_by_id(db, accompany_id=accompany_id)
    if not accompany:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을수 없습니다.")
    if accompany.leader_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")

    image_creates = []
    image_hashes = set()
    if images:
        for image in images:
            image_hash = file_utils.calculate_image_hash(image)
            if image_hash in image_hashes:
                continue  # 이미 처리된 이미지 해시라면 스킵
            image_hashes.add(image_hash)

            existing_image = accompany_crud.get_image_by_hash(db, image_hash)
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
                                                             tags_accompany=tag_creates, qna=qna, accompany_id=accompany_id)

    accompany_crud.update_accompany(db, db_accompany=accompany, accompany_update=accompany_update_data)


@router.post("/create/notice", status_code=status.HTTP_204_NO_CONTENT, tags=["Accompany"])
def accompany_create_notice(accompany_id: int, _notice_create: notice_schema.NoticeCreate, token: str = Header(),
                            db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    if current_user.suspension_period and current_user.suspension_period > datetime.now():
        raise HTTPException(status_code=403, detail="User is currently suspended")

    accompany = accompany_crud.get_accompany_by_id(db, accompany_id=accompany_id)
    if not accompany:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"동행을 찾을 수 없습니다.")

    if current_user.id != accompany.leader_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")

    topic = f'{accompany.id}_notice'

    message = messaging.Message(
        notification=messaging.Notification(
            title='📢리더가 새로운 공지를 등록했습니다!',
            body=_notice_create.content,
        ),
        data={
            "accompany_id": str(accompany.id)
        },
        android=messaging.AndroidConfig(
            priority='high',
            notification=messaging.AndroidNotification(
                sound='default'
            )
        ),
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    sound='default',
                    content_available=True
                )
            )
        ),
        topic=topic
    )

    messaging.send(message)

    notice_crud.create_accompany_notice(db, accompany_id=accompany_id, notice_create=_notice_create)


@router.put("/update/notice", status_code=status.HTTP_204_NO_CONTENT, tags=["Accompany"])
def accompany_update_notice(_notice_update: notice_schema.NoticeUpdate, token: str = Header(),
                            db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    if current_user.suspension_period and current_user.suspension_period > datetime.now():
        raise HTTPException(status_code=403, detail="User is currently suspended")

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

    application_list = accompany_crud.get_application_list(db, accompany_id=accompany_id)

    for application in application_list:
        user = user_crud.get_user_by_id(db, user_id=application.user_id)
        if user.lang_level is None:
            user.lang_level = {}
    return application_list


@router.post("/apply", status_code=status.HTTP_204_NO_CONTENT, tags=["Accompany"])
def accompany_apply(application_create: accompany_schema.ApplicationCreate, token: str = Header(),
                    db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)
    accompany = accompany_crud.get_accompany_by_id(db, accompany_id=application_create.accompany_id)
    if not accompany:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Accompany not found.")

    if application_create.answer is None:
        if accompany.qna:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Answer should be required.")
        accompany_crud.register_accompany(db, accompany_id=accompany.id, user=current_user)
    else:
        if accompany.qna is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Answer do not needed.")
        accompany_crud.apply_accompany(db, accompany=accompany,
                                       user_id=current_user.id, answer=application_create.answer)

    leader = user_crud.get_user_by_id(db, user_id=accompany.leader_id)

    message = messaging.Message(
        notification=messaging.Notification(
            title='🙋🏻내 동행에 새로운 지원자가 있어요!',
            body=application_create.answer,
        ),
        data={
            "accompany_id": str(accompany.id)
        },
        android=messaging.AndroidConfig(
            priority='high',
            notification=messaging.AndroidNotification(
                sound='default'
            )
        ),
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    sound='default',
                    content_available=True
                )
            )
        ),
        token=leader.fcm_token
    )

    messaging.send(message)


@router.put("/application/approve/{application_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Accompany"])
def application_approve(application_id: int, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)
    application = accompany_crud.get_application_by_id(db, application_id=application_id)
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Application not found.")
    if current_user.id != application.accompany.leader_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the leader can approve applications.")
    accompany_crud.approve_application(db, application_id=application_id)

    accompany = accompany_crud.get_accompany_by_id(db, accompany_id=application.accompany_id)
    member = user_crud.get_user_by_id(db, user_id=application.user_id)

    message = messaging.Message(
        notification=messaging.Notification(
            title=f'🎉동행 {accompany.title}의 멤버가 되었어요!',
            body='축하합니다! 이제 내 동행을 보러 가보실까요?',
        ),
        data={
            "accompany_id": str(accompany.id)
        },
        android=messaging.AndroidConfig(
            priority='high',
            notification=messaging.AndroidNotification(
                sound='default'
            )
        ),
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    sound='default',
                    content_available=True
                )
            )
        ),
        token=member.fcm_token
    )

    messaging.send(message)


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

    members = accompany_crud.get_members_by_accompany_id(db, accompany_id=accompany_id)

    if current_user.id == accompany.leader_id:
        if members:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="리더는 동행을 탈퇴할 수 없습니다.")
        else:
            accompany_crud.delete_accompany(db, accompany_id=accompany_id)
            return

    if current_user not in members:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")

    accompany_crud.leave_accompany(db, accompany_id=accompany_id, member=current_user)


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

    accompany_crud.ban_accompany_member(db, accompany_id=accompany.id, member=member)


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

    accompany_crud.assign_new_leader(db, accompany=accompany, member=member)

    message = messaging.Message(
        notification=messaging.Notification(
            title=f'😎동행 {accompany.title}의 리더가 되었어요!',
            body='리더가 되면 여러 권한이 생겨요. 모임을 잘 이끌어주세요~!',
        ),
        data={
            "accompany_id": str(accompany.id)
        },
        android=messaging.AndroidConfig(
            priority='high',
            notification=messaging.AndroidNotification(
                sound='default'
            )
        ),
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    sound='default',
                    content_available=True
                )
            )
        ),
        token=member.fcm_token
    )

    messaging.send(message)
