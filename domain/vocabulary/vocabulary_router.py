from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.vocabulary import vocabulary_schema
from domain.vocabulary import vocabulary_crud
from domain.user import user_crud


router = APIRouter(
    prefix="/api/vocabulary",
)


@router.get("/list", response_model=list[vocabulary_schema.Vocabulary], tags=["Vocabulary"])
def vocabulary_list(db: Session = Depends(get_db), page: int = 0, size: int = 10):
    total_pages, _voca_list = vocabulary_crud.get_vocabulary_list(db, start_index=page * size, limit=size)

    for voca in _voca_list:
        voca.total_pages = total_pages

    return _voca_list


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT, tags=["Vocabulary"])
def vocabulary_create(_vocabulary_create: vocabulary_schema.VocabularyCreate, token: str = Header(),
                      db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    if current_user.suspension_period and current_user.suspension_period > datetime.now():
        raise HTTPException(status_code=403, detail="User is currently suspended")

    vocabulary_crud.create_vocabulary(db, vocabulary_create=_vocabulary_create, user=current_user)
