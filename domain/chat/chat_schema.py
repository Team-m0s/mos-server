from pydantic import BaseModel, field_validator

from domain.post.post_schema import Post


class AccompanyChat(BaseModel):
    accompany_id: int
    message: str


class PersonalChat(BaseModel):
    sender_id: str
    receiver_id: str
    is_anonymous: bool
    message: str