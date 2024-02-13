from pydantic import BaseModel, field_validator
import datetime
from enum import Enum
from typing import List
from models import ActivityScope
from domain.user.user_schema import UserBase


class ImageBase(BaseModel):
    id: int
    image_url: str


class TagBase(BaseModel):
    id: int
    name: str


class NoticeBase(BaseModel):
    id: int
    content: str


class AccompanyBase(BaseModel):
    id: int
    title: str
    city: str
    total_member: int
    leader_id: int
    leader: UserBase
    member: list[UserBase] = []
    images: List[ImageBase] = []
    tags: List[TagBase] = []
    notices: List[NoticeBase] = []
    introduce: str
    activity_scope: ActivityScope
    create_date: datetime.datetime
    update_date: datetime.datetime | None
    chat_count: int
    like_count: int

