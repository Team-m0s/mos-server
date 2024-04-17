from pydantic import BaseModel, field_validator


class BlockedList(BaseModel):
    blocked_uuid: str
    blocked_firebase_uuid: str


class BlockUser(BaseModel):
    blocked_uuid: str | None
    blocked_firebase_uuid: str | None
