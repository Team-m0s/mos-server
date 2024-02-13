from pydantic import BaseModel, field_validator
from typing import Dict


class LanguageLevel(BaseModel):
    level: Dict[str, int]


class PostUser(BaseModel):
    nickName: str
    profile_img: str


class CommentUser(BaseModel):
    nickName: str
    profile_img: str


class UserBase(BaseModel):
    nickName: str
    profile_img: str
    lang_level: Dict[str, int]

    class Config:
        orm_mode = True


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
