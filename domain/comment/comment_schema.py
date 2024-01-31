from pydantic import BaseModel, field_validator
import datetime


class CommentCreate(BaseModel):
    content: str

    @field_validator('content')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('빈 값은 허용되지 않습니다.')
        return v


class Comment(BaseModel):
    id: int
    content: str
    create_date: datetime.datetime
