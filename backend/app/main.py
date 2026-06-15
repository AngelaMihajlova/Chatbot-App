import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError

from app.api.v1.router import router
from app.core.config import settings
from app.db.base import Base
from app.db.init_db import init_db
from app.db.models import Document, DocumentGroup, Group, SystemConfig, User, UserGroup  # noqa: F401 — ensure models are registered
from app.db.session import SessionLocal, engine
from app.services import history as history_svc
from app.services import storage as storage_svc
from app.services.vector import ensure_collection


def _wait_for_db(retries: int = 10, delay: float = 3.0) -> None:
    for attempt in range(retries):
        try:
            with engine.connect():
                return
        except OperationalError:
            if attempt == retries - 1:
                raise
            print(f"DB not ready, retrying in {delay}s… ({attempt + 1}/{retries})")
            time.sleep(delay)


def _retry(fn, label: str, retries: int = 15, delay: float = 3.0):
    for attempt in range(retries):
        try:
            fn()
            return
        except Exception as exc:
            if attempt == retries - 1:
                raise
            print(f"{label} not ready ({exc.__class__.__name__}), retrying in {delay}s… ({attempt + 1}/{retries})")
            time.sleep(delay)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(">> waiting for DB")
    _wait_for_db()
    print(">> creating tables")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print(">> seeding DB")
        init_db(db)
        print(">> ensuring Qdrant collection")
        _retry(ensure_collection, "Qdrant")
        print(">> ensuring MinIO bucket")
        _retry(lambda: storage_svc.ensure_bucket(db), "MinIO")
        print(">> ensuring DynamoDB tables")
        _retry(lambda: history_svc.ensure_tables(db), "DynamoDB")
        print(">> startup complete")
    finally:
        db.close()
    yield


app = FastAPI(title="Company Chatbot API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}
