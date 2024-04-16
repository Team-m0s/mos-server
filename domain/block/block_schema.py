from pydantic import BaseModel, field_validator


class BlockedList(BaseModel):
    blocked_uuid: str


class BlockUser(BaseModel):
    blocked_uuid: str
