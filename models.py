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

    # 닉네임, 좋아요 추가 필요


class Comment(Base):
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    create_date = Column(DateTime, nullable=False)
    post_id = Column(Integer, ForeignKey("post.id"))
    post = relationship("Post", backref="comments")


