from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from domain.admin import admin_crud

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
)