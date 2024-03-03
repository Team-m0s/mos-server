from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List
from datetime import datetime, date

from utils import file_utils
from models import Accompany, User, Image, Tag, accompany_member, ActivityScope, Category, Application
from domain.accompany.accompany_schema import AccompanyCreate, AccompanyUpdate, TagCreate, ImageCreate


def get_accompany_list(db: Session, search_keyword: str = None, sort_order: str = 'latest'):
    query = db.query(Accompany)

    if search_keyword:
        # Accompany와 Tag를 연결하는 조인을 생성
        query = query.outerjoin(Tag, Accompany.id == Tag.accompany_id)

        keyword_filter = or_(Accompany.title.ilike(f"%{search_keyword}%"), Tag.name.ilike(f"%{search_keyword}%"))
        query = query.filter(keyword_filter)

        query = query.group_by(Accompany.id)

    if sort_order == 'oldest':
        query = query.order_by(Accompany.create_date.asc())
    elif sort_order == 'popularity':
        query = query.order_by(Accompany.like_count.desc())
    else:
        query = query.order_by(Accompany.create_date.desc())

    accompany_list = query.all()
    return accompany_list


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

    if category is not None:
        query = query.filter(Accompany.category.in_(category))

    return query.all()


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

    for image in accompany_create.images_accompany:
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

    images_to_delete = [image for image in current_images
                        if image.image_hash not in [img.image_hash for img in submitted_images]]
    images_to_add = [image for image in submitted_images
                     if image.image_hash not in [img.image_hash for img in current_images]]

    tags_to_delete = [tag for tag in current_tags
                      if tag.name not in [t.name for t in submitted_tags]]
    tags_to_add = [tag for tag in submitted_tags
                   if tag.name not in [t.name for t in current_tags]]

    # Delete images
    for image in images_to_delete:
        # 이미지가 다른 accompany에서 사용중이면 저장소에서는 삭제 X
        other_image = get_image_by_hash(db, image_hash=image.image_hash)
        if other_image and other_image.accompany_id != db_accompany.id:
            continue

        # Check if the image exists in the database
        image_in_db = db.query(Image).filter(Image.id == image.id).first()
        if image_in_db is None:
            continue

        # Check if the image file deletion is successful
        try:
            file_utils.delete_image_file(image.image_url)
        except Exception as e:
            print(f"Failed to delete image file: {e}")
            continue

        db.delete(image)

    # Add new images
    for image in images_to_add:
        db_image = Image(image_url=image.image_url, image_hash=image.image_hash, accompany_id=db_accompany.id)
        db.add(db_image)

    # Delete tags
    for tag in tags_to_delete:
        db.delete(tag)

    # Add new tags
    for tag in tags_to_add:
        db_tag = Tag(name=tag.name, accompany_id=db_accompany.id)
        db.add(db_tag)

    db.commit()


def apply_accompany(db: Session, accompany_id: int, user_id: int, answer: str):
    db_application = Application(accompany_id=accompany_id, user_id=user_id,
                                 answer=answer, apply_date=date.today())
    db.add(db_application)
    db.commit()


def get_application_by_id(db: Session, application_id: int):
    return db.query(Application).filter(Application.id == application_id).all()


def approve_application(db: Session, application_id: int):
    application = db.query(Application).filter(Application.id == application_id).first()
    if application:
        db.execute(accompany_member.insert().values(user_id=application.user_id,
                                                    application_id=application.accompany_id))
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
