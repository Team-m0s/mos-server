from pydantic import BaseModel, field_validator
import datetime
from domain.comment.comment_schema import NoticeComment
from domain.user.user_schema import NoticeUser


class NoticeBase(BaseModel):
    id: int
    user: NoticeUser
    content: str
    create_date: datetime.datetime
    update_date: datetime.datetime | None
    comment_notices: list[NoticeComment] = []
    is_blinded: bool | None


class NoticeCreate(BaseModel):
    content: str

    @field_validator('content')
    def content_length(cls, v):
        if not v or len(v.strip()) < 2:  # 공백을 제외한 길이가 2글자 미만인 경우
            raise ValueError('내용은 공백 제외 2글자 이상이어야 합니다.')
        if len(v) > 1000:  # 공백 포함 길이가 1000글자를 초과하는 경우
            raise ValueError('내용은 공백 포함 1000글자 이하이어야 합니다.')
        return v


class NoticeUpdate(NoticeCreate):
    notice_id: int


class NoticeDelete(BaseModel):
    notice_id: int

