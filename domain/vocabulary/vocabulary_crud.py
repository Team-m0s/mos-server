import math
from datetime import datetime
from sqlalchemy.orm import Session
from models import Vocabulary, User, Comment

from domain.vocabulary.vocabulary_schema import VocabularyCreate


def get_vocabulary_list(db: Session, start_index: int = 0, limit: int = 10):
    query = db.query(Vocabulary)

    total = query.count()
    total_pages = math.ceil(total / limit)

    _voca_list = query.offset(start_index).limit(limit).all()

    for voca in _voca_list:
        voca.comment_count = db.query(Comment).filter(Comment.vocabulary_id == voca.id).count()
    return total_pages, _voca_list


def get_vocabulary(db: Session, vocabulary_id: int, start_index: int = 0, limit: int = 10):
    vocabulary = db.query(Vocabulary).get(vocabulary_id)

    comments_query = db.query(Comment).filter(Comment.vocabulary_id == vocabulary_id)
    total_comments = comments_query.count()
    total_pages = math.ceil(total_comments / limit) if limit > 0 else 0

    vocabulary.comment_vocabularies = comments_query.offset(start_index).limit(limit).all()
    vocabulary.total_pages = total_pages

    return vocabulary


def get_vocabulary_by_id(db: Session, vocabulary_id: int):
    return db.query(Vocabulary).filter(Vocabulary.id == vocabulary_id).first()


def create_vocabulary(db: Session, vocabulary_create: VocabularyCreate, user: User):
    db_vocabulary = Vocabulary(subject=vocabulary_create.subject,
                               content=vocabulary_create.content,
                               create_date=datetime.now(),
                               author=user,)
    db.add(db_vocabulary)
    db.commit()