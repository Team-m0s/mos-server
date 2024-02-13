from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from models import Accompany


def get_accompany_list(db: Session):
    accompany_list = db.query(Accompany).order_by(Accompany.id.desc()).all()
    return accompany_list

