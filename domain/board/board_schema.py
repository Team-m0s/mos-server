from pydantic import BaseModel, field_validator
from typing import Optional
import datetime


class Board(BaseModel):
    id: int
    parent_id: Optional[int]
    create_date: datetime.datetime
    title: str
    latest_post_date: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

