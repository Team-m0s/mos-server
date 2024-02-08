import datetime
from domain.user.user_schema import PostUser
from pydantic import BaseModel, field_validator
from domain.comment.comment_schema import Comment
from domain.board.board_schema import PostBoard


class Post(BaseModel):
    id: int
    board: PostBoard | None
    user: PostUser | None
    subject: str
    content: str
    like_count: int
    content_img: str
    is_anonymous: bool
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
