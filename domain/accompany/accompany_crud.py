from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List
from datetime import datetime

from utils import file_utils
from models import Accompany, User, Image, Tag, accompany_member
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


def get_accompany_by_id(db: Session, accompany_id: int):
    return db.query(Accompany).filter(Accompany.id == accompany_id).first()


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
                             update_date=datetime.now())
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
        file_utils.delete_image_file(image.image_url)
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


def ban_accompany_member(db: Session, accompany_id: int, member_id: int):
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
