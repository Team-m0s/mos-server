from datetime import datetime

from models import Board
from sqlalchemy.orm import Session


def get_board_list(db: Session):
    board_list = db.query(Board).order_by(Board.id.desc()).all()
    return board_list


def get_board(db: Session, board_id: int):
    board = db.query(Board).get(board_id)
    return board


def create_board(db: Session, title: str, parent_id: int = None):
    db_board = Board(title=title,
                     parent_id=parent_id,
                     create_date=datetime.now())
    db.add(db_board)
    db.commit()