from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from domain.post import post_router

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
