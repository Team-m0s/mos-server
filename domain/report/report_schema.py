from pydantic import BaseModel, field_validator
from models import ReportReasonBoard, ReportReasonChat, ReportReasonAccompany
from typing import List


class ReportCreate(BaseModel):
    report_reason: List[ReportReasonBoard] | None
    other: str | None

    @field_validator('other')
    def check_length(cls, v):
        if v is not None:
            if len(v.strip()) < 1 or len(v) > 100:
                raise ValueError('신고 사유는 공백 제외 1글자 이상, 공백 포함 100글자 이하만 가능합니다.')
        return v


class PostReport(ReportCreate):
    post_id: int


class CommentReport(ReportCreate):
    comment_id: int


class AccompanyReport(BaseModel):
    report_reason: List[ReportReasonAccompany] | None
    other: str | None
    accompany_id: int


class NoticeReport(BaseModel):
    report_reason: List[ReportReasonAccompany] | None
    other: str | None
    notice_id: int


class VocabularyReport(ReportCreate):
    vocabulary_id: int


class UserReport(ReportCreate):
    reported_user_id: int


class UserFeedback(BaseModel):
    content: str


class AccompanyChatReport(BaseModel):
    accompany_id: int
    message_id: str
    report_reason: List[ReportReasonChat] | None
    other: str | None


class PersonalChatReport(BaseModel):
    talk_id: str
    report_reason: List[ReportReasonChat] | None
    other: str | None
