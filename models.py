from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, Enum, Table
from sqlalchemy.orm import relationship

from pydantic import BaseModel
from database import Base
from datetime import datetime

import enum


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    uuid = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    email = Column(String, nullable=False)
    nickName = Column(String, nullable=False)
    profile_img = Column(String, nullable=True)
    point = Column(Integer, nullable=False, default=0)
    lang_level = Column(JSON, nullable=True)
    report_count = Column(Integer, nullable=False, default=0)


class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True)
    subject = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    like_count = Column(Integer, default=0)
    is_anonymous = Column(Boolean, nullable=False, default=True)
    report_count = Column(Integer, nullable=False, default=0)
    create_date = Column(DateTime, nullable=False)
    modify_date = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", backref="post_users")
    board_id = Column(Integer, ForeignKey("board.id"))
    board = relationship("Board", backref="post_boards")


class Comment(Base):
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, nullable=True)
    content = Column(Text, nullable=False)
    like_count = Column(Integer, default=0)
    create_date = Column(DateTime, nullable=False)
    modify_date = Column(DateTime, nullable=True)
    is_anonymous = Column(Boolean, nullable=False, default=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", backref="comment_users")
    post_id = Column(Integer, ForeignKey("post.id"))
    post = relationship("Post", backref="comment_posts")
    notice_id = Column(Integer, ForeignKey("notice.id"))
    notice = relationship("Notice", backref="comment_notices")


class Like(Base):
    __tablename__ = "like"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", backref="like_users")
    post_id = Column(Integer, ForeignKey("post.id"))
    post = relationship("Post", backref="like_posts")
    comment_id = Column(Integer, ForeignKey("comment.id"))
    comment = relationship("Comment", backref="like_comments")
    accompany_id = Column(Integer, ForeignKey("accompany.id"))
    accompany = relationship("Accompany", backref="like_accompanies")


class Board(Base):
    __tablename__ = "board"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    create_date = Column(DateTime, nullable=False)
    parent_id = Column(Integer, nullable=True)


class ActivityScope(enum.Enum):
    online = "온라인"
    offline = "오프라인"
    hybrid = "온오프라인"


class Category(enum.Enum):
    activity = '액티비티'
    cultureArt = '문화 ･ 예술'
    hobby = '취미생활'
    musicInstrument = '음악 ･ 악기'
    volunteering = '봉사활동'
    oneDayClass = '원데이 클래스'
    parentingPet = '육아 ･ 반려동물'
    foodTour = '맛집 투어'
    languageExchange = '언어 교환'
    game = '게임 ･ 오락'
    exerciseSport = '운동 ･ 스포츠'
    booksSelfImprovement = '책 ･ 자기계발'
    dating = '연애'
    others = '기타'


accompany_member = Table(
    'accompany_member',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('accompany_id', Integer, ForeignKey('accompany.id'), primary_key=True)
)


class Accompany(Base):
    __tablename__ = "accompany"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    city = Column(String, nullable=False)
    total_member = Column(Integer, nullable=False)
    leader_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', backref="accompany_users")
    member = relationship('User', secondary=accompany_member, backref='accompany_members')
    introduce = Column(String, nullable=False)
    activity_scope = Column(Enum(ActivityScope), nullable=False)
    create_date = Column(String, nullable=False)
    update_date = Column(String, nullable=False)
    category = Column(Enum(Category), nullable=False)
    chat_count = Column(Integer, nullable=False, default=0)
    like_count = Column(Integer, nullable=False, default=0)


class Image(Base):
    __tablename__ = "image"
    id = Column(Integer, primary_key=True)
    image_url = Column(String, nullable=False)
    image_hash = Column(String, nullable=False)
    post_id = Column(Integer, ForeignKey("post.id"))
    post = relationship("Post", backref="images_post")
    accompany_id = Column(Integer, ForeignKey("accompany.id"))
    accompany = relationship("Accompany", backref="images_accompany")


class Tag(Base):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    accompany_id = Column(Integer, ForeignKey("accompany.id"))
    accompany = relationship("Accompany", backref="tags_accompany")


class Notice(Base):
    __tablename__ = "notice"
    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    create_date = Column(DateTime, nullable=False)
    update_date = Column(DateTime, nullable=True)
    accompany_id = Column(Integer, ForeignKey("accompany.id"))
    accompany = relationship("Accompany", backref="notices_accompany")