import datetime
from domain.user.user_schema import PostUser
from pydantic import BaseModel, field_validator
from typing import Optional, List
from domain.comment.comment_schema import Comment
from domain.board.board_schema import Board
from domain.accompany.accompany_schema import ImageCreate, ImageBase


class PostDetail(BaseModel):
    id: int
    board: Board | None
    user: PostUser | None
    subject: str
    content: str
    like_count: int
    is_liked_by_user: bool = False
    is_bookmarked_by_user: bool = False
    image_urls: List[ImageBase] = []
    is_anonymous: bool
    is_blinded: bool | None
    create_date: datetime.datetime
    modify_date: datetime.datetime | None
    comment_count: int
    comment_posts: list[Comment] = []

    class Config:
        from_attributes = True


class Post(BaseModel):
    id: int
    board: Board | None
    user: PostUser | None
    subject: str
    content: str
    like_count: int
    is_liked_by_user: bool = False
    image_urls: List[ImageBase] = []
    is_anonymous: bool
    is_blinded: bool
    create_date: datetime.datetime
    modify_date: datetime.datetime | None
    comment_count: int
    total_pages: int = 0


class PostList(BaseModel):
    total_pages: int = 0
    post_list: list[Post] = []


class PostCreate(BaseModel):
    subject: str
    content: str
    images_post: Optional[List[ImageCreate]] = None
    is_anonymous: bool

    @field_validator('subject')
    def subject_length(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('제목은 공백 제외 2글자 이상이어야 합니다.')
        return v

    @field_validator('content')
    def content_length(cls, v):
        if not v or len(v.strip()) < 5:
            raise ValueError('내용은 공백 제외 5글자 이상이어야 합니다.')
        return v


class PostUpdate(PostCreate):
    post_id: int


class PostDelete(BaseModel):
    post_id: int
