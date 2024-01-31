from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from domain.post import post_router
from domain.comment import comment_router
from domain.like import like_router

app = FastAPI()

origins = [
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/hello")
def hello():
    return {"message": "안녕하세요 파이보"}


app.include_router(post_router.router)
app.include_router(comment_router.router)
app.include_router(like_router.router)
