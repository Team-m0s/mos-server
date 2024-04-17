from pydantic import BaseModel
from models import ReportReason
from typing import List


class PostReport(BaseModel):
    post_id: int
    report_reason: List[ReportReason] | None
    other: str | None


class CommentReport(BaseModel):
    comment_id: int
    report_reason: List[ReportReason] | None
    other: str | None


class AccompanyReport(BaseModel):
    accompany_id: int
    report_reason: List[ReportReason] | None
    other: str | None


class NoticeReport(BaseModel):
    notice_id: int
    report_reason: List[ReportReason] | None
    other: str | None


class UserReport(BaseModel):
    reported_user_id: int
    report_reason: List[ReportReason] | None
    other: str | None


class AccompanyChatReport(BaseModel):
    accompany_id: int
    message_id: str
    report_reason: List[ReportReason] | None
    other: str | None


class PersonalChatReport(BaseModel):
    talk_id: str
    report_reason: List[ReportReason] | None
    other: str | None
