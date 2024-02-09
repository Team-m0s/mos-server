from models import Board
from sqlalchemy.orm import Session


def get_board_list(db: Session):
    board_list = db.query(Board).order_by(Board.id.desc()).all()
    return board_list


def get_board(db: Session, board_id: int):
    board = db.query(Board).get(board_id)
    return board
