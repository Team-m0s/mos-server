# 나의 python 버전
FROM python:3.10.7

# /code 폴더 만들기
WORKDIR /mos-server

# ./requirements.txt 를 /code/requirements.txt 로 복사
COPY ./requirements.txt /mos-server/requirements.txt

# requirements.txt 를 보고 모듈 전체 설치(-r)
RUN pip install --no-cache-dir -r /mos-server/requirements.txt

# 현재 디렉토리의 모든 파일을 /code 로 복사
COPY ./ /mos-server/

# 실행
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${BIND_PORT} main:app --worker-class uvicorn.workers.UvicornWorker --access-logfile ./errorLog.log"]
