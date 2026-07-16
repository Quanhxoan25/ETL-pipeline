from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

host = os.getenv("PG_HOST", "localhost")
database = os.getenv("PG_DATABASE")
user = os.getenv("PG_USERNAME")
password = os.getenv("PG_PASSWORD")
port = os.getenv("PG_PORT", "5432")

DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

engine = create_engine(DATABASE_URL, pool_size=10,max_overflow=20, pool_recycle=1800)


SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()