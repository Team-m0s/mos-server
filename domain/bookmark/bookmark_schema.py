from pydantic import BaseModel, field_validator

from domain.post.post_schema import Post


class Bookmark(BaseModel):
    id: int
    total_pages: int = 0
    post: Post
