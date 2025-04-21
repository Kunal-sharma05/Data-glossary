import os
import stat
from fastapi import FastAPI, Response, Request
from contextlib import asynccontextmanager
import logging
from db.database import engine
from db.database import base
from fastapi.middleware.cors import CORSMiddleware
from routers.data import router as data_router
from routers.user import router as user_router
from starlette.middleware.sessions import SessionMiddleware
from utility.Data_glossary import process_document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

secret_key = os.getenv("SECRET_KEY")


@asynccontextmanager
async def lifespan(app: FastAPI):
    vector_store = process_document()
    yield
    vector_store.index.reset()
    if os.path.exists("faiss_index"):
        try:
            os.chmod("faiss_index", stat.S_IWRITE)
            os.remove("faiss_index")
            print(f"FAISS index deleted")
        except Exception as e:
            print(f"Error deleting FAISS index: {e}")
        else:
            print(f"no index found ")


app = FastAPI(lifespan=lifespan, debug=True)

base.metadata.create_all(bind=engine)

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"]
)

app.add_middleware(
    SessionMiddleware,
    secret_key=secret_key,
    session_cookie="session_id",
    max_age=3600,
    https_only=False if os.getenv("ENV") == "development" else True
)
app.include_router(data_router, tags=["LLM RESPONSE"])
app.include_router(user_router, tags=["User Data"])


# @app.middleware("http")
# async def bypass_options_validation(request: Request, call_next):
#     if request.method == "OPTIONS":
#         return Response(status_code=200)
#     return await call_next(request)
