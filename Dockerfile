# 나의 python 버전
FROM python:3.10.7

# /code 폴더 만들기
WORKDIR /code

# ./requirements.txt 를 /code/requirements.txt 로 복사
COPY ./requirements.txt /code/requirements.txt

# requirements.txt 를 보고 모듈 전체 설치(-r)
RUN pip install --no-cache-dir -r /code/requirements.txt

# 현재 디렉토리의 모든 파일을 /code 로 복사
COPY ./ /code/

# 실행
CMD ["gunicorn", "--bind", "0:8000", "app.main:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--daemon", "--access-logfile", "./errorLog.log"]
