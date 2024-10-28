from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse
import os
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware

import auth
from utils import db_utils
from domain.user import user_crud
from domain.post import post_router
from domain.comment import comment_router
from domain.like import like_router
from domain.user import user_router
from domain.board import board_router
from domain.accompany import accompany_router
from domain.bookmark import bookmark_router
from domain.report import report_router
from domain.chat import chat_router
from domain.notification import notification_router
from domain.block import block_router
from domain.vocabulary import vocabulary_router
from domain.admin import admin_router

load_dotenv()

origins = [
    "*",
]

app = FastAPI()

SECRET_KEY = os.getenv("SECRET_KEY")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="/mos-server/static"), name="static")
#app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def main():
    return HTMLResponse(content="<h1>환영합니다</h1>", status_code=200)


scheduler = BackgroundScheduler()
scheduler.add_job(db_utils.delete_blinded_contents, 'cron', hour=0, minute=0)
scheduler.add_job(user_crud.delete_user_sso, 'cron', hour=0, minute=0)
scheduler.start()

app.include_router(post_router.router)
app.include_router(comment_router.router)
app.include_router(like_router.router)
app.include_router(user_router.router)
app.include_router(board_router.router)
app.include_router(accompany_router.router)
app.include_router(bookmark_router.router)
app.include_router(report_router.router)
app.include_router(chat_router.router)
app.include_router(notification_router.router)
app.include_router(block_router.router)
app.include_router(vocabulary_router.router)
app.include_router(admin_router.router)
app.include_router(auth.router)