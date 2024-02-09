from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.board import board_schema, board_crud

router = APIRouter(
    prefix="/api/board",
)


@router.get("/list", response_model=list[board_schema.Board], tags=["Board"])
def board_list(db: Session = Depends(get_db)):
    _board_list = board_crud.get_board_list(db)
    return _board_list

