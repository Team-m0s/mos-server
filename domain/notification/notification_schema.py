from pydantic import BaseModel, field_validator
import datetime


class Notification(BaseModel):
    id: int
    title: str
    body: str
    post_id: int | None
    vocabulary_id: int | None
    accompany_id: int | None
    create_date: datetime.datetime
    total_pages: int = 0
    is_read: bool
    is_Post: bool
