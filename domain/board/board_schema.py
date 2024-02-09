from pydantic import BaseModel, field_validator


class Board(BaseModel):
    id: int
    parent_id: int | None
    title: str

