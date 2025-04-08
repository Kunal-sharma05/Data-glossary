import os
from sqlmodel import create_engine, Session
from dotenv import load_dotenv
from typing import Annotated
from fastapi import Depends

load_dotenv()

USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
DB_NAME = os.getenv("DB_NAME")
PORT = os.getenv("PORT")

database_url = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
engine = create_engine(database_url)


def get_db():
    with Session(engine) as session:
        yield session


db_dependency = Annotated[Session, Depends(get_db)]
