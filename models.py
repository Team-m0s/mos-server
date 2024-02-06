from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
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
    content_img = Column(String, nullable=True)
    is_anonymous = Column(Boolean, nullable=False, default=True)
    report_count = Column(Integer, nullable=False, default=0)
    create_date = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", backref="posts")
    board_id = Column(Integer, ForeignKey("board.id"))
    board = relationship("Board", backref="posts")
    # 닉네임, 좋아요 추가 필요


class Comment(Base):
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, nullable=True)
    content = Column(Text, nullable=False)
    like_count = Column(Integer, default=0)
    create_date = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", backref="comments")
    post_id = Column(Integer, ForeignKey("post.id"))
    post = relationship("Post", backref="comments")


class Like(Base):
    __tablename__ = "like"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", backref="likes")
    post_id = Column(Integer, ForeignKey("post.id"))
    post = relationship("Post", backref="likes")
    comment_id = Column(Integer, ForeignKey("comment.id"))
    comment = relationship("Comment", backref="likes")


class Board(Base):
    __tablename__ = "board"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    parent_id = Column(Integer, nullable=True)



