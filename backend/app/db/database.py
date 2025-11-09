
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_URL = "sqlite:///./items.db"
connect_args = {"check_same_thread": False}  

engine = create_engine(DB_URL, echo=False, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
