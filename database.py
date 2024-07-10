from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://mos_admin:REMOVED@mos-server-db-rds.cbkqmgeusqyw.ap-northeast-2.rds" \
                          ".amazonaws.com/mosAPI"

#SQLALCHEMY_DATABASE_URL = "postgresql://postgres:REMOVED@localhost/postgres"

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"options": "-c timezone=Asia/Seoul"}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
