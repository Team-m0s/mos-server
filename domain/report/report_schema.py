from pydantic import BaseModel
from models import ReportReason


class PostReport(BaseModel):
    post_id: int
    report_reason: ReportReason
    other: str | None


class CommentReport(BaseModel):
    comment_id: int
    report_reason: ReportReason
    other: str | None


class UserReport(BaseModel):
    reported_user_id: int
    report_reason: ReportReason
    other: str | None
