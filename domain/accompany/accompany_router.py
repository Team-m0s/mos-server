from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from domain.accompany import accompany_schema, accompany_crud
from domain.user import user_crud


router = APIRouter(
    prefix="/api/accompany"
)


@router.get("/list", response_model=list[accompany_schema.AccompanyBase], tags=["Accompany"])
def accompany_list(db: Session = Depends(get_db)):
    _accompany_list = accompany_crud.get_accompany_list(db)

    for accompany in _accompany_list:
        leader = user_crud.get_user_by_id(db, user_id=accompany.leader_id)
        accompany.leader = leader
        accompany.member = [member for member in accompany.member if member.id != accompany.leader_id]
    return _accompany_list
