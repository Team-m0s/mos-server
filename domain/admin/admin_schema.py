import datetime

from pydantic import BaseModel, field_validator
from typing import Optional
from domain.report.report_schema import FeedbackBase
from models import InsightCategory


class InsightBase(BaseModel):
    id: int
    title: str
    content: str
    main_image: str | None
    category: str
    create_date: datetime.datetime | None


class InsightListResponse(BaseModel):
    total_insights: int
    insights: list[InsightBase]


class FeedbackListResponse(BaseModel):
    total_feedbacks: int
    feedbacks: list[FeedbackBase]


class InsightCreate(BaseModel):
    title: str
    content: str
    main_image: str | None
    category: InsightCategory


class InsightUpdate(InsightCreate):
    insight_id: int


class InsightDelete(BaseModel):
    insight_id: int


class BannerBase(BaseModel):
    title: str
    image: str | None
    destinationPage: str
    isTop: bool | None
    create_date = datetime.datetime


class BannerCreate(BaseModel):
    title: str
    image: str | None
    destinationPage: str
    isTop: bool | None


class BannerUpdate(BannerCreate):
    banner_id: int


class BannerDelete(BaseModel):
    banner_id: int
