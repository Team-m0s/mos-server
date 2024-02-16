from pydantic import BaseModel, field_validator
import datetime
from enum import Enum
from typing import List, Optional
from models import ActivityScope, Tag, Image, Notice
from domain.user.user_schema import UserBase
from domain.notice.notice_schema import NoticeBase
from models import ActivityScope, Category


class ImageBase(BaseModel):
    id: int
    image_url: str


class ImageCreate(BaseModel):
    image_url: str
    image_hash: str


class TagBase(BaseModel):
    id: int
    name: str


class TagCreate(BaseModel):
    name: str

    @field_validator('name')
    def name_length(cls, v):
        if not v or len(v.strip()) < 2:  # 공백을 제외한 길이가 2글자 미만인 경우
            raise ValueError('내용은 공백 제외 2글자 이상이어야 합니다.')
        if len(v) > 8:
            raise ValueError('내용은 공백 포함 8글자 이하이어야 합니다.')
        return v


class AccompanyBase(BaseModel):
    id: int
    category: Category
    title: str
    city: str
    total_member: int
    leader_id: int
    leader: UserBase
    member: list[UserBase] = []
    image_urls: List[ImageBase] = []
    tags_accompany: List[TagBase] = []
    notices_accompany: List[NoticeBase] = []
    introduce: str
    activity_scope: ActivityScope
    create_date: datetime.datetime
    update_date: datetime.datetime | None
    chat_count: int
    like_count: int


class AccompanyCreate(BaseModel):
    category: Category
    title: str
    activity_scope: ActivityScope
    images_accompany: Optional[List[ImageCreate]] = None
    city: str
    introduce: str
    total_member: int
    tags_accompany: Optional[List[TagCreate]] = None

    @field_validator('title')
    def content_length(cls, v):
        if not v or len(v.strip()) < 2:  # 공백을 제외한 길이가 2글자 미만인 경우
            raise ValueError('내용은 공백 제외 2글자 이상이어야 합니다.')
        if len(v) > 30:  # 공백 포함 길이가 30글자를 초과하는 경우
            raise ValueError('내용은 공백 포함 30글자 이하이어야 합니다.')
        return v

    @field_validator('introduce')
    def introduce_length(cls, v):
        if not v or len(v.strip()) < 2:  # 공백을 제외한 길이가 2글자 미만인 경우
            raise ValueError('내용은 공백 제외 2글자 이상이어야 합니다.')
        if len(v) > 1000:
            raise ValueError('내용은 공백 포함 1000글자 이하이어야 합니다.')
        return v


