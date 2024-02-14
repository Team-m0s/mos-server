from pydantic import BaseModel, field_validator
import datetime
from enum import Enum
from typing import List
from models import ActivityScope, Tag, Image, Notice
from domain.user.user_schema import UserBase
from models import ActivityScope


class ImageBase(BaseModel):
    id: int
    image_url: str


class ImageCreate(BaseModel):
    image_url: str


class TagBase(BaseModel):
    id: int
    name: str


class TagCreate(BaseModel):
    name: str


class NoticeBase(BaseModel):
    id: int
    content: str


class NoticeCreate(BaseModel):
    content: str


class AccompanyBase(BaseModel):
    id: int
    title: str
    city: str
    total_member: int
    leader_id: int
    leader: UserBase
    member: list[UserBase] = []
    images_accompany: List[ImageBase] = []
    tags_accompany: List[TagBase] = []
    notices_accompany: List[NoticeBase] = []
    introduce: str
    activity_scope: ActivityScope
    create_date: datetime.datetime
    update_date: datetime.datetime | None
    chat_count: int
    like_count: int


class AccompanyCreate(BaseModel):
    category: str
    title: str
    activity_scope: ActivityScope
    images_accompany: List[ImageCreate] = []
    city: str
    introduce: str
    total_member: int
    tags_accompany: List[TagCreate] = []


