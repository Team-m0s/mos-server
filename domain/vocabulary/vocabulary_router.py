from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.vocabulary import vocabulary_schema
from domain.vocabulary import vocabulary_crud
from domain.user import user_crud
from firebase_admin import messaging

router = APIRouter(
    prefix="/api/vocabulary",
)


@router.get("/list", response_model=list[vocabulary_schema.Vocabulary], tags=["Vocabulary"])
def vocabulary_list(db: Session = Depends(get_db), page: int = 0, size: int = 10):
    total_pages, _voca_list = vocabulary_crud.get_vocabulary_list(db, start_index=page * size, limit=size)

    for voca in _voca_list:
        voca.total_pages = total_pages

    return _voca_list


@router.get("/detail/{vocabulary_id}", response_model=vocabulary_schema.VocabularyDetail, tags=["Vocabulary"])
def vocabulary_detail(vocabulary_id: int, page: int = 0, size: int = 10, db: Session = Depends(get_db)):
    total_pages, vocabulary = vocabulary_crud.get_vocabulary(db, vocabulary_id, start_index=page * size, limit=size)
    if vocabulary is None:
        raise HTTPException(status_code=404, detail="Vocabulary not found")

    for comment in vocabulary.comment_vocabularies:
        comment.total_pages = total_pages
    return vocabulary


@router.put("/solve/{vocabulary_id}", response_model=vocabulary_schema.VocabularyDetail, tags=["Vocabulary"])
def solve_vocabulary(vocabulary_id: int, user_id: int, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    vocabulary = vocabulary_crud.get_vocabulary_by_id(db, vocabulary_id=vocabulary_id)
    if not vocabulary:
        raise HTTPException(status_code=404, detail="Vocabulary not found")
    if current_user.id != vocabulary.author.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    vocabulary_crud.mark_vocabulary_as_solved(db, vocabulary=vocabulary, user_id=user_id)

    total_pages, vocabulary = vocabulary_crud.get_vocabulary(db, vocabulary_id)

    solver = user_crud.get_user_by_id(db, user_id)

    message = messaging.Message(
        notification=messaging.Notification(
            title='🎊 내 답변이 채택되었어요!',
            body=vocabulary.subject,
        ),
        data={
            "vocabulary_id": str(vocabulary.id)
        },
        android=messaging.AndroidConfig(
            priority='high',
            notification=messaging.AndroidNotification(
                sound='default'
            )
        ),
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    # badge=badge_count,
                    sound='default',
                    content_available=True
                )
            )
        ),
        token=solver.fcm_token
    )

    messaging.send(message)

    for comment in vocabulary.comment_vocabularies:
        comment.total_pages = total_pages

    return vocabulary


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT, tags=["Vocabulary"])
def vocabulary_create(_vocabulary_create: vocabulary_schema.VocabularyCreate, token: str = Header(),
                      db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    if current_user.suspension_period and current_user.suspension_period > datetime.now():
        raise HTTPException(status_code=403, detail="User is currently suspended")

    vocabulary_crud.create_vocabulary(db, vocabulary_create=_vocabulary_create, user=current_user)


@router.put("/update", status_code=status.HTTP_204_NO_CONTENT, tags=["Vocabulary"])
def vocabulary_update(_vocabulary_update: vocabulary_schema.VocabularyUpdate, token: str = Header(),
                      db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    if current_user.suspension_period and current_user.suspension_period > datetime.now():
        raise HTTPException(status_code=403, detail="User is currently suspended")

    vocabulary = vocabulary_crud.get_vocabulary_by_id(db, vocabulary_id=_vocabulary_update.vocabulary_id)

    if not vocabulary:
        raise HTTPException(status_code=404, detail="Vocabulary not found")

    if current_user.id != vocabulary.author.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    vocabulary_crud.update_vocabulary(db, db_vocabulary=vocabulary, vocabulary_update=_vocabulary_update)


@router.delete("/delete/{vocabulary_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Vocabulary"])
def delete_vocabulary(vocabulary_id: int, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    vocabulary = vocabulary_crud.get_vocabulary_by_id(db, vocabulary_id=vocabulary_id)
    if not vocabulary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vocabulary not found")
    if current_user.id != vocabulary.author.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    if vocabulary.is_solved:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solved vocabulary cannot be deleted")

    vocabulary_crud.delete_vocabulary(db, vocabulary=vocabulary)
