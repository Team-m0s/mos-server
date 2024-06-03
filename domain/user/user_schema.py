import datetime

from pydantic import BaseModel, field_validator
from typing import Dict, Optional, List


class ImageCreate(BaseModel):
    image_url: str
    image_hash: Optional[str] = None


class AuthSchema(BaseModel):
    fcm_token: str
    provider: str
    nick_name: str | None
    language_preference: str | None

    @field_validator('nick_name')
    def validate_nick_name(cls, v):
        if v:
            if len(v) < 2 or len(v) > 10:
                raise ValueError('닉네임은 최소 2글자 이상, 10글자 이하만 가능합니다.')
            if v.strip() != v:
                raise ValueError('닉네임에는 공백을 포함할 수 없습니다.')
        return v


class LanguagePref(BaseModel):
    language_preference: str


class LanguageLevel(BaseModel):
    level: Dict[str, int]


class UserList(BaseModel):
    email: str
    nickName: str
    register_date: datetime.datetime


class UserListResponse(BaseModel):
    total_users: int
    users: List[UserList]


class PostUser(BaseModel):
    uuid: str
    user_code: str
    firebase_uuid: str
    nickName: str
    profile_img: str | None


class CommentUser(BaseModel):
    id: int
    uuid: str
    user_code: str
    firebase_uuid: str
    nickName: str
    profile_img: str | None


class NoticeUser(BaseModel):
    id: int
    uuid: str
    nickName: str
    profile_img: str | None


class FeedbackUser(BaseModel):
    email: str


class UserBase(BaseModel):
    id: int
    uuid: str
    nickName: str
    profile_img: str | None
    introduce: str | None
    lang_level: Dict[str, int]
    firebase_uuid: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    nickname: str

    @field_validator('nickname')
    # 빈 값은 허용하지 않으면서, 7글자 이하로 제한, 특수문자 입력 불가
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('빈 값은 허용되지 않습니다.')
        if len(v) > 7:
            raise ValueError('7글자 이하로 입력해주세요.')
        if not v.isalnum():
            raise ValueError('특수문자는 입력할 수 없습니다.')
        return v


class UserUpdate(BaseModel):
    id: int
    nickName: str
    images_user: Optional[ImageCreate] = None
    lang_level: Dict[str, int] | None
    introduce: str | None

    @field_validator('nickName')
    def validate_nick_name(cls, v):
        if v:
            if len(v) < 2 or len(v) > 10:
                raise ValueError('닉네임은 최소 2글자 이상, 10글자 이하만 가능합니다.')
            if v.strip() != v:
                raise ValueError('닉네임에는 공백을 포함할 수 없습니다.')
        return v
