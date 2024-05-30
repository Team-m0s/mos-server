from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.admin import admin_crud
from domain.user import user_crud
from domain.user import user_schema
from domain.admin import admin_schema
from utils import file_utils

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
)


@router.get("/user/lists", response_model=user_schema.UserListResponse)
def user_list(token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    total_users, users = admin_crud.get_all_users(db)
    return {"total_users": total_users, "users": users}


@router.get("/feedback/lists", response_model=admin_schema.FeedbackListResponse)
def feedback_list(token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    #if not current_user.is_admin:
    #    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    total_feedbacks, feedbacks = admin_crud.get_all_feedbacks(db)
    return {"total_feedbacks": total_feedbacks, "feedbacks": feedbacks}


@router.get("/insights", response_model=admin_schema.InsightListResponse)
def insight_lists(db: Session = Depends(get_db), search_keyword_title: str = None, search_keyword_content: str = None,
                  search_keyword_title_exact: str = None, search_keyword_content_exact: str = None):
    total_insights, insights = admin_crud.get_insights(db, search_keyword_title, search_keyword_content,
                                                       search_keyword_title_exact, search_keyword_content_exact)
    return {"total_insights": total_insights, "insights": insights}


@router.post("/upload/images")
def upload_images(images: List[UploadFile] = File(), token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    #if not current_user.is_admin:
    #    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    image_url = []
    for image in images:
        image_path = file_utils.save_image_file(image)
        image_url.append(f"https://www.mos-server.store/static/{image_path}")

    return image_url


@router.post("/create/insight", status_code=status.HTTP_204_NO_CONTENT)
def insight_create(_insight_create: admin_schema.InsightCreate, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    admin_crud.create_insight(db, insight_create=_insight_create)


@router.put("/update/insight", status_code=status.HTTP_204_NO_CONTENT)
def insight_update(_insight_update: admin_schema.InsightUpdate, token: str = Header(), db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)

    db_insight = admin_crud.get_insight_by_id(db, insight_id=_insight_update.insight_id)

    if not db_insight:
        raise HTTPException(status_code=404, detail="Insight not found")

    admin_crud.update_insight(db, db_insight=db_insight, insight_update=_insight_update)


@router.delete("/delete/insight", status_code=status.HTTP_204_NO_CONTENT)
def insight_delete(_insight_delete: admin_schema.InsightDelete, token: str = Header(),
                   db: Session = Depends(get_db)):
    current_user = user_crud.get_current_user(db, token)
    db_insight = admin_crud.get_insight_by_id(db, insight_id=_insight_delete.insight_id)

    if not db_insight:
        raise HTTPException(status_code=404, detail="Insight not found")

    admin_crud.delete_insight(db, db_insight=db_insight)
