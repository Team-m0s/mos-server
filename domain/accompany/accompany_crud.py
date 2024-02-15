from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from datetime import datetime

from models import Accompany, User, Image, Tag, accompany_member
from domain.accompany.accompany_schema import AccompanyCreate, TagCreate, ImageCreate


def get_accompany_list(db: Session):
    accompany_list = db.query(Accompany).order_by(Accompany.id.desc()).all()
    return accompany_list


def get_accompany_by_id(db: Session, accompany_id: int):
    return db.query(Accompany).filter(Accompany.id == accompany_id).first()


def get_image_by_accompany_id(db: Session, accompany_id: int):
    return db.query(Image).filter(Image.accompany_id == accompany_id).all()


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
        db_image = Image(image_url=image.image_url, accompany_id=db_accompany.id)
        db.add(db_image)

    for tag in accompany_create.tags_accompany:
        print(tag.name)
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


