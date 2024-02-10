from pydantic import BaseModel, field_validator
import datetime


class Board(BaseModel):
    id: int
    parent_id: int | None
    create_date: datetime.datetime
    title: str

