from datetime import datetime

from domain.post.post_schema import PostCreate, PostUpdate
from models import Post, User, Board, Comment, Image
from sqlalchemy.orm import Session
from sqlalchemy import or_
import domain.accompany.accompany_crud


def get_post_list(db: Session, board_id: int = 0, start_index: int = 0, limit: int = 10,
                  search_keyword: str = None, sort_order: str = 'newest'):
    query = db.query(Post)
    if board_id != 0:
        query = query.filter(Post.board_id == board_id)
    if search_keyword:
        keyword_filter = or_(Post.subject.ilike(f"%{search_keyword}%"), Post.content.ilike(f"%{search_keyword}%"))
        query = query.filter(keyword_filter)

    if sort_order == 'oldest':
        query = query.order_by(Post.create_date.asc())
    elif sort_order == 'likes':
        query = query.order_by(Post.like_count.desc())
    else:
        query = query.order_by(Post.create_date.desc())

    total = query.count()
    _post_list = query.offset(start_index).limit(limit).all()
    return total, _post_list


def get_post(db: Session, post_id: int, comment_sort_order: str = 'oldest'):
    post = db.query(Post).get(post_id)

    if post:
        if comment_sort_order == 'newest':
            comments = db.query(Comment).filter(Comment.post_id == post.id).order_by(Comment.create_date.desc()).all()
        else:
            comments = db.query(Comment).filter(Comment.post_id == post.id).order_by(Comment.create_date.asc()).all()

        post.comment_posts = comments

    return post


def create_post(db: Session, post_create: PostCreate, board: Board, user: User):
    db_post = Post(board=board,
                   subject=post_create.subject,
                   content=post_create.content,
                   is_anonymous=post_create.is_anonymous,
                   create_date=datetime.now(),
                   user=user)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    for image in post_create.images_post:
        db_image = Image(image_url=image.image_url, post_id=db_post.id)
        db.add(db_image)

    db.commit()


def update_post(db: Session, db_post: Post, post_update: PostUpdate):
    db_post.subject = post_update.subject
    db_post.content = post_update.content
    db_post.content_img = post_update.content_img
    db_post.is_anonymous = post_update.is_anonymous
    db_post.modify_date = datetime.now()
    db.add(db_post)
    db.commit()


def delete_post(db: Session, db_post: Post):
    db.delete(db_post)
    db.commit()
