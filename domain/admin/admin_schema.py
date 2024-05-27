from pydantic import BaseModel, field_validator
from typing import Optional


class InsightBase(BaseModel):
    id: int
    content: str


class InsightCreate(BaseModel):
    title: str
    content: str
