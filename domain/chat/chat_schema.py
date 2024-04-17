from pydantic import BaseModel, field_validator

from domain.post.post_schema import Post


class AccompanyChat(BaseModel):
    id: int


class PersonalChat(BaseModel):
    sender_id: str
    receiver_id: str
    is_anonymous: bool
    message: str
