import datetime

from pydantic import BaseModel, field_validator
from domain.comment.comment_schema import Comment


class Post(BaseModel):
    id: int
    nickname: str
    subject: str
    content: str
    create_date: datetime.datetime
    comments: list[Comment] = []


class PostCreate(BaseModel):
    subject: str
    content: str

    @field_validator('subject', 'content')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('빈 값은 허용되지 않습니다.')
        return v
