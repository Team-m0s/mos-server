from pydantic import BaseModel, field_validator

from domain.post.post_schema import Post


class AccompanyChat(BaseModel):
    id: int
    post: Post