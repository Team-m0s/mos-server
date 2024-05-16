from pydantic import BaseModel, field_validator
import datetime
from enum import Enum
from typing import List, Optional
from domain.user.user_schema import UserBase
from domain.notice.notice_schema import NoticeBase
from models import ActivityScope, Category


class ImageBase(BaseModel):
    id: int
    image_url: str


class ImageCreate(BaseModel):
    image_url: str
    image_hash: Optional[str] = None


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


class ApplicationBase(BaseModel):
    id: int
    user: UserBase
    answer: str
    apply_date: str


class ApplicationCreate(BaseModel):
    accompany_id: int
    answer: Optional[str] = None

    @field_validator('answer')
    def name_length(cls, v):
        if v is not None:
            if len(v) < 6 or len(v) > 500:  # 공백을 제외한 길이가 2글자 미만인 경우
                raise ValueError('내용은 공백 포함 6글자 이상 500글자 이하이어야 합니다.')
            return v


class AccompanyBase(BaseModel):
    id: int
    category: Category
    title: str
    city: str
    total_member: int
    application_count: Optional[int] = None
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
    is_like_by_user: bool = False
    is_blinded: bool | None
    total_pages: int = 0
    qna: str | None


class AccompanyCreate(BaseModel):
    category: Category
    title: str
    activity_scope: ActivityScope
    images_accompany: Optional[List[ImageCreate]] = None
    city: Optional[str] = None
    introduce: str
    total_member: int
    tags_accompany: Optional[List[TagCreate]] = None
    qna: Optional[str] = None

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


class AccompanyUpdate(AccompanyCreate):
    accompany_id: int
