import math

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, date

from utils import file_utils
from models import Accompany, User, Image, Tag, accompany_member, ActivityScope, Application, Like
from domain.accompany.accompany_schema import AccompanyCreate, AccompanyUpdate, ImageBase, TagCreate, Category
from domain.user.user_crud import get_user_by_id


def get_accompany_list(db: Session, is_closed: bool, start_index: int = 0, limit: int = 10,
                       search_keyword: str = None, category: Category = None, sort_order: str = 'latest'):
    query = db.query(Accompany)

    if not is_closed:
        query = query.filter(Accompany.is_closed == is_closed)

    if search_keyword:
        # Accompany와 Tag를 연결하는 조인을 생성
        query = query.outerjoin(Tag, Accompany.id == Tag.accompany_id)

        keyword_filter = or_(Accompany.title.ilike(f"%{search_keyword}%"), Tag.name.ilike(f"%{search_keyword}%"))
        query = query.filter(keyword_filter)

        query = query.group_by(Accompany.id)

    if category is not None and category.value != '전체':
        query = query.filter(Accompany.category == category)

    if sort_order == 'oldest':
        query = query.order_by(Accompany.create_date.asc())
    elif sort_order == 'popularity':
        query = query.order_by(Accompany.like_count.desc())
    else:
        query = query.order_by(Accompany.create_date.desc())

    total = query.count()
    total_pages = math.ceil(total / limit)

    accompany_list = query.offset(start_index).limit(limit).all()
    return total_pages, accompany_list


def get_accompany_filtered_list(db: Session, is_closed: bool, total_member: List[int],
                                activity_scope: ActivityScope = None, city: str = None,
                                category: List[Category] = None):
    query = db.query(Accompany)

    if not is_closed:
        query = query.filter(Accompany.is_closed == is_closed)

    if total_member is not None and len(total_member) == 2:
        query = query.filter(and_(Accompany.total_member >= total_member[0], Accompany.total_member <= total_member[1]))

    if activity_scope is not None:
        query = query.filter(Accompany.activity_scope == activity_scope)

    if city is not None:
        query = query.filter(Accompany.city.ilike(f"%{city}%"))  # 수정된 부분

    if category is not None and len(category) > 0:
        query = query.filter(Accompany.category.in_(category))

    accompany_list = query.all()
    return accompany_list


def get_accompany_detail(db: Session, accompany_id: int):
    accompany = db.query(Accompany).get(accompany_id)
    return accompany


def get_accompanies_by_user_id(db: Session, user_id: int):
    # 사용자가 leader인 동행들 조회
    leader_accompanies = db.query(Accompany).filter(Accompany.leader_id == user_id).all()

    # 사용자가 member인 동행들 조회
    member_accompanies = db.query(Accompany).join(accompany_member, Accompany.id == accompany_member.c.accompany_id) \
        .filter(accompany_member.c.user_id == user_id).all()

    all_accompanies = leader_accompanies + member_accompanies

    # 결과를 modify_date 필드를 기준으로 정렬
    all_accompanies.sort(key=lambda accompany: accompany.update_date, reverse=True)

    return all_accompanies


def set_accompany_detail(db: Session, accompany_list: List[Accompany]):
    for accompany in accompany_list:
        leader = get_user_by_id(db, user_id=accompany.leader_id)
        if leader.lang_level is None:
            leader.lang_level = {}
        accompany.leader = leader
        accompany.member = [member for member in accompany.member if member.id != accompany.leader_id]
        for member in accompany.member:
            if member.lang_level is None:
                member.lang_level = {}

        # 이미지 설정
        images = get_image_by_accompany_id(db, accompany_id=accompany.id)
        accompany.image_urls = [
            ImageBase(id=image.id, image_url=f"https://www.mos-server.store/static/{image.image_url}")
            for image in images if image.image_url] if images else []

    return accompany_list


def get_application_list(db: Session, accompany_id: int):
    return db.query(Application).filter(Application.accompany_id == accompany_id).all()


def get_accompany_by_id(db: Session, accompany_id: int):
    return db.query(Accompany).filter(Accompany.id == accompany_id).first()


def get_members_by_accompany_id(db: Session, accompany_id: int):
    return db.query(User).join(accompany_member, User.id == accompany_member.c.user_id) \
        .filter(accompany_member.c.accompany_id == accompany_id).all()


def get_tag_by_accompany_id(db: Session, accompany_id: int):
    return db.query(Tag).filter(Tag.accompany_id == accompany_id).all()


def get_image_by_accompany_id(db: Session, accompany_id: int):
    return db.query(Image).filter(Image.accompany_id == accompany_id).all()


def get_image_by_hash(db: Session, image_hash: str):
    return db.query(Image).filter(Image.image_hash == image_hash).first()


def get_image_by_hash_all(db: Session, image_hash: str):
    return db.query(Image).filter(Image.image_hash == image_hash).all()


def create_accompany(db: Session, accompany_create: AccompanyCreate, user: User):
    db_accompany = Accompany(title=accompany_create.title,
                             category=accompany_create.category,
                             city=accompany_create.city,
                             total_member=accompany_create.total_member,
                             leader_id=user.id,
                             introduce=accompany_create.introduce,
                             activity_scope=accompany_create.activity_scope,
                             create_date=datetime.now(),
                             update_date=datetime.now(),
                             qna=accompany_create.qna)
    db.add(db_accompany)
    db.commit()
    db.refresh(db_accompany)

    # 중복된 이미지 제거
    unique_images = {img.image_hash: img for img in accompany_create.images_accompany}.values()

    for image in unique_images:
        db_image = Image(image_url=image.image_url, image_hash=image.image_hash, accompany_id=db_accompany.id)
        db.add(db_image)

    for tag in accompany_create.tags_accompany:
        db_tag = Tag(name=tag.name, accompany_id=db_accompany.id)
        db.add(db_tag)

    db.commit()


def update_accompany(db: Session, db_accompany: Accompany, accompany_update: AccompanyUpdate):
    db_accompany.title = accompany_update.title
    db_accompany.category = accompany_update.category
    db_accompany.city = accompany_update.city
    db_accompany.activity_scope = accompany_update.activity_scope
    db_accompany.introduce = accompany_update.introduce
    db_accompany.total_member = accompany_update.total_member
    db_accompany.update_date = datetime.now()

    current_images = get_image_by_accompany_id(db, accompany_id=db_accompany.id)
    submitted_images = accompany_update.images_accompany

    current_tags = get_tag_by_accompany_id(db, accompany_id=db_accompany.id)
    submitted_tags = accompany_update.tags_accompany

    # 중복 이미지 해시 제거 (동일한 image_hash를 가진 이미지는 하나만 남김)
    unique_submitted_images = {img.image_hash: img for img in submitted_images}.values()

    current_image_hashes = {img.image_hash for img in current_images}
    submitted_image_hashes = {img.image_hash for img in unique_submitted_images}

    current_tag_names = {tag.name for tag in current_tags}
    submitted_tag_names = {tag.name for tag in submitted_tags}

    # 이미지 처리
    for now_image in current_images:
        if now_image.image_hash not in submitted_image_hashes:
            # 다른 accompany에서 사용 여부 확인
            other_images = get_image_by_hash_all(db, image_hash=now_image.image_hash)
            if any(image.accompany_id != db_accompany.id for image in other_images):
                db.delete(now_image)
                continue

            image_in_db = db.query(Image).filter(Image.id == now_image.id).first()
            if image_in_db is None:
                continue

            # 이미지 파일 삭제 시도
            try:
                file_utils.delete_image_file(now_image.image_url)
            except Exception as e:
                print(f"Failed to delete image file: {e}")
            else:
                db.delete(now_image)

    # 새로운 이미지 추가
    for image in unique_submitted_images:
        if image.image_hash not in current_image_hashes:
            db_image = Image(image_url=image.image_url, image_hash=image.image_hash, accompany_id=db_accompany.id)
            db.add(db_image)

    # 태그 처리
    for now_tag in current_tags:
        if now_tag.name not in submitted_tag_names:
            db.delete(now_tag)

    for tag_name in submitted_tag_names - current_tag_names:
        db_tag = Tag(name=tag_name, accompany_id=db_accompany.id)
        db.add(db_tag)

    db.commit()


def apply_accompany(db: Session, accompany_id: int, user_id: int, answer: str):
    db_application = Application(accompany_id=accompany_id, user_id=user_id,
                                 answer=answer, apply_date=date.today())
    db.add(db_application)
    db.commit()


def register_accompany(db: Session, accompany_id: int, user_id: int):
    db.execute(accompany_member.insert().values(user_id=user_id, accompany_id=accompany_id))
    db.commit()


def get_application_by_id(db: Session, application_id: int):
    return db.query(Application).filter(Application.id == application_id).first()


def approve_application(db: Session, application_id: int):
    application = db.query(Application).filter(Application.id == application_id).first()
    if application:
        db.execute(accompany_member.insert().values(user_id=application.user_id,
                                                    accompany_id=application.accompany_id))
        db.delete(application)
        db.commit()


def reject_application(db: Session, application_id: int):
    application = db.query(Application).filter(Application.id == application_id).first()
    if application:
        # Delete the application
        db.delete(application)
        db.commit()


def ban_accompany_member(db: Session, accompany_id: int, member_id: int):
    db.query(accompany_member).filter(
        and_(
            accompany_member.c.user_id == member_id,
            accompany_member.c.accompany_id == accompany_id
        )
    ).delete(synchronize_session=False)
    db.commit()


def leave_accompany(db: Session, accompany_id: int, member_id: int):
    db.query(accompany_member).filter(
        and_(
            accompany_member.c.user_id == member_id,
            accompany_member.c.accompany_id == accompany_id
        )
    ).delete(synchronize_session=False)
    db.commit()


def assign_new_leader(db: Session, accompany_id: int, member_id: int):
    accompany = db.query(Accompany).filter(Accompany.id == accompany_id).first()
    old_leader_id = accompany.leader_id
    accompany.leader_id = member_id

    db.execute(accompany_member.insert().values(user_id=old_leader_id, accompany_id=accompany_id))
    ban_accompany_member(db, accompany_id=accompany_id, member_id=member_id)
    db.commit()
