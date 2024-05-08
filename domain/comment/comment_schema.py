from pydantic import BaseModel, field_validator
from domain.user.user_schema import CommentUser, UserBase
from typing import Optional
import datetime


class CommentCreate(BaseModel):
    author_uuid: str
    content: str
    is_anonymous: bool

    @field_validator('content')
    def not_empty(cls, v):
        if not v or not len(v.strip()) < 2:
            raise ValueError('댓글은 공백 제외 2글자 이상이어야 합니다.')
        if len(v) > 800:
            raise ValueError('댓글은 공백 포함 800글자 이하이어야 합니다.')
        return v


class SubCommentCreate(CommentCreate):
    pass


class NoticeCommentCreate(BaseModel):
    content: str

    @field_validator('content')
    def not_empty(cls, v):
        if not v or not len(v.strip()) < 2:
            raise ValueError('댓글은 공백 제외 2글자 이상이어야 합니다.')
        if len(v) > 800:
            raise ValueError('댓글은 공백 포함 800글자 이하이어야 합니다.')
        return v


class VocaCommentCreate(BaseModel):
    content: str

    @field_validator('content')
    def not_empty(cls, v):
        if not v or not len(v.strip()) < 2:
            raise ValueError('댓글은 공백 제외 2글자 이상이어야 합니다.')
        if len(v) > 800:
            raise ValueError('댓글은 공백 포함 800글자 이하이어야 합니다.')
        return v


class Comment(BaseModel):
    id: int
    parent_id: int | None
    content: str
    like_count: int
    is_liked_by_user: bool = False
    is_anonymous: bool
    is_blinded: bool | None
    user: CommentUser | None
    create_date: datetime.datetime
    modify_date: datetime.datetime | None
    post_id: int
    sub_comments_count: Optional[int] = None
    total_pages: int = 0


class NoticeComment(BaseModel):
    id: int
    parent_id: int | None
    content: str
    like_count: int
    is_liked_by_user: bool = False
    is_anonymous: bool
    is_blinded: bool
    user: CommentUser | None
    create_date: datetime.datetime
    modify_date: datetime.datetime | None


class VocabularyComment(BaseModel):
    id: int
    content: str
    user: CommentUser | None
    create_date: datetime.datetime
    total_pages: int = 0


class CommentUpdate(CommentCreate):
    comment_id: int


class CommentDelete(BaseModel):
    comment_id: int
