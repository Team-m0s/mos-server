import datetime

from pydantic import BaseModel


class Post(BaseModel):
    id: int
    nickname: str
    subject: str
    content: str
    create_date: datetime.datetime
