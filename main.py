from fastapi import FastAPI
from db.database import engine
from sqlmodel import SQLModel
from fastapi.middleware.cors import CORSMiddleware
from routers.data import router as data

app = FastAPI()

SQLModel.metadata.create_all(engine)

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(data, tags=["Data"])