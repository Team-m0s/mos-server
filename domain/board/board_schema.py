from pydantic import BaseModel, field_validator


class PostBoard(BaseModel):
    id: int

