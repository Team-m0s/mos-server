import math
from datetime import datetime
from sqlalchemy.orm import Session
from models import Vocabulary, User, Comment, Notification

from domain.vocabulary.vocabulary_schema import VocabularyCreate, VocabularyUpdate
from domain.user import user_crud


def get_vocabulary_list(db: Session, start_index: int = 0, limit: int = 10):
    query = db.query(Vocabulary).order_by(Vocabulary.create_date.desc())

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
    vocabulary.comment_count = total_comments

    if vocabulary.is_solved:
        solved_user_comment = db.query(Comment).filter(Comment.user_id == vocabulary.solved_user_id,
                                                       Comment.vocabulary_id == vocabulary_id).first()
        vocabulary.solved_user_comment = solved_user_comment

    return total_pages, vocabulary


def get_vocabulary_by_id(db: Session, vocabulary_id: int):
    return db.query(Vocabulary).filter(Vocabulary.id == vocabulary_id).first()


def get_vocabulary_message_title(language_preference: str, message_type: str):
    titles = {
        'voca_solved': {
            '한국어': '🎊 내 답변이 채택되었어요!',
            'English': '🎊 Your answer has been accepted!',
            # Add more languages here
        },
    }

    return titles[message_type].get(language_preference, titles[message_type]['English'])


def create_vocabulary(db: Session, vocabulary_create: VocabularyCreate, user: User):
    user_crud.add_user_activity_and_points(db, user=user, activity_type='vocabulary', activity_limit=5,
                                           activity_point=2)

    db_vocabulary = Vocabulary(subject=vocabulary_create.subject,
                               content=vocabulary_create.content,
                               create_date=datetime.now(),
                               author=user, )
    db.add(db_vocabulary)
    db.commit()


def update_vocabulary(db: Session, db_vocabulary: Vocabulary, vocabulary_update: VocabularyUpdate):
    db_vocabulary.subject = vocabulary_update.subject
    db_vocabulary.content = vocabulary_update.content

    db.add(db_vocabulary)
    db.commit()


def delete_vocabulary(db: Session, vocabulary: Vocabulary):
    if vocabulary.author.point >= 2:
        vocabulary.author.point -= 2
    elif vocabulary.author.point < 2:
        vocabulary.author.point = 0

    db.delete(vocabulary)
    db.commit()


def mark_vocabulary_as_solved(db: Session, vocabulary: Vocabulary, user_id: int):
    solved_user = db.query(User).filter(User.id == user_id).first()

    vocabulary.author.point += 3
    solved_user.point += 10

    vocabulary.is_solved = True
    vocabulary.solved_user_id = user_id

    db_notification = Notification(translation_key='answerAccepted',
                                   title='',
                                   body=vocabulary.subject,
                                   vocabulary_id=vocabulary.id,
                                   create_date=datetime.now(),
                                   is_Post=False,
                                   user_id=user_id)
    db.add(db_notification)

    db.commit()
