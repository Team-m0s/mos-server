from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True)
    nickname = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    create_date = Column(DateTime, nullable=False)
    like_count = Column(Integer, default=0)

    # 닉네임, 좋아요 추가 필요


class Comment(Base):
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    create_date = Column(DateTime, nullable=False)
    like_count = Column(Integer, default=0)
    post_id = Column(Integer, ForeignKey("post.id"))
    post = relationship("Post", backref="comments")


class Like(Base):
    __tablename__ = "like"

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("post.id"))
    post = relationship("Post", backref="likes")
    comment_id = Column(Integer, ForeignKey("comment.id"))
    comment = relationship("Comment", backref="likes")



