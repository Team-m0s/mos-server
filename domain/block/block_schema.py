from pydantic import BaseModel, field_validator
from typing import Optional


class BlockedList(BaseModel):
    blocked_uuid: str
    blocked_firebase_uuid: str


class BlockUser(BaseModel):
    blocked_uuid: Optional[str]
    blocked_firebase_uuid: Optional[str]
