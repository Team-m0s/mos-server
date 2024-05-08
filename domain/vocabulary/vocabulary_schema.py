import datetime

from pydantic import BaseModel, field_validator
from domain.comment.comment_schema import VocabularyComment
from domain.user.user_schema import PostUser
from typing import Optional


class VocabularyDetail(BaseModel):
    id: int
    author: PostUser | None
    subject: str
    content: str
    is_solved: bool
    create_date: datetime.datetime
    solved_user_comment: Optional[VocabularyComment] = None
    comment_count: int
    comment_vocabularies: list[VocabularyComment] = []

    class Config:
        from_attributes = True


class Vocabulary(BaseModel):
    id: int
    subject: str
    content: str
    is_solved: bool
    create_date: datetime.datetime
    comment_count: int
    total_pages: int = 0


class VocabularyCreate(BaseModel):
    subject: str
    content: str

    @field_validator('subject')
    def subject_length(cls, v):
        if not v or len(v.strip()) < 1 or len(v.strip()) > 10:
            raise ValueError('제목은 공백 제외 1글자 이상, 10글자 이하이어야 합니다.')
        return v

    @field_validator('content')
    def content_length(cls, v):
        if not v or len(v.strip()) < 2 or len(v.strip()) > 100:
            raise ValueError('내용은 공백 제외 2글자 이상, 100글자 이하이어야 합니다.')
        return v
