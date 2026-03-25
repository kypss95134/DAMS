from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 建立 MySQL 連線 (帳號 root, 密碼 1234, 資料庫 dams_db)
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:1234@localhost/dams_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency，用於 FastAPI 路由取得 db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
