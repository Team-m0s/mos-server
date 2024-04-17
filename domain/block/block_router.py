from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.block.block_schema import BlockedList, BlockUser
from domain.block import block_crud
from domain.user import user_crud


router = APIRouter(
    prefix="/api/block",
)


@router.get("/list", response_model=list[str], tags=["Block"])
def blocked_list(token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)
    blocked_lists = block_crud.get_blocked_list(db, user=current_user)

    result = []
    for block in blocked_lists:
        if block.blocked_uuid is not None:
            result.append(block.blocked_uuid)
        elif block.blocked_firebase_uuid is not None:
            result.append(block.blocked_firebase_uuid)

    return result


@router.post("/user", status_code=status.HTTP_204_NO_CONTENT, tags=["Block"])
def block_user(create_user_block: BlockUser, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    if create_user_block.blocked_uuid:
        blocked_user = user_crud.get_user_by_uuid(db, uuid=create_user_block.blocked_uuid)
    else:
        blocked_user = user_crud.get_user_by_firebase_uuid(db, uuid=create_user_block.blocked_firebase_uuid)

    if not blocked_user:
        raise HTTPException(status_code=404, detail="User not found")

    block_crud.block_user(db, user=current_user, blocked_user=create_user_block)
