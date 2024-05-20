from datetime import datetime

from models import Board
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Post


def get_board_list(db: Session):
    subquery = (
        db.query(
            Post.board_id,
            func.max(Post.create_date).label('latest_post_date')
        )
        .group_by(Post.board_id)
        .subquery()
    )

    board_list = (
        db.query(
            Board,
            subquery.c.latest_post_date
        )
        .outerjoin(subquery, Board.id == subquery.c.board_id)
        .order_by(Board.id.desc())
        .all()
    )

    # Pydantic 모델로 변환
    result = [
        {
            "id": board.id,
            "create_date": board.create_date,
            "title": board.title,
            "latest_post_date": latest_post_date
        }
        for board, latest_post_date in board_list
    ]

    return result


def get_board(db: Session, board_id: int):
    board = db.query(Board).get(board_id)
    return board


def create_board(db: Session, title: str):
    db_board = Board(title=title,
                     create_date=datetime.now())
    db.add(db_board)
    db.commit()