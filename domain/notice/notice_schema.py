from pydantic import BaseModel, field_validator
import datetime


class NoticeBase(BaseModel):
    id: int
    content: str
    create_date: datetime.datetime


class NoticeCreate(BaseModel):
    content: str

    @field_validator('content')
    def content_length(cls, v):
        if not v or len(v.strip()) < 2:  # 공백을 제외한 길이가 2글자 미만인 경우
            raise ValueError('내용은 공백 제외 2글자 이상이어야 합니다.')
        if len(v) > 1000:  # 공백 포함 길이가 1000글자를 초과하는 경우
            raise ValueError('내용은 공백 포함 1000글자 이하이어야 합니다.')
        return v
