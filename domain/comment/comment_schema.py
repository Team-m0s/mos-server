from pydantic import BaseModel, field_validator
from domain.user.user_schema import CommentUser
import datetime


class CommentCreate(BaseModel):
    content: str
    is_anonymous: bool

    @field_validator('content')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('빈 값은 허용되지 않습니다.')
        return v


class Comment(BaseModel):
    id: int
    parent_id: int | None
    content: str
    like_count: int
    user: CommentUser | None
    create_date: datetime.datetime
    modify_date: datetime.datetime | None
    post_id: int
