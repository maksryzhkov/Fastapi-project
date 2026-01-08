from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, HttpUrl
from datetime import datetime
import secrets
import os
from fastapi.responses import RedirectResponse

# Создаем директорию для данных, если её нет
try:
    os.makedirs("/app/data", exist_ok=True)
except PermissionError:
    # Если нет прав, продолжаем - возможно, директория уже создана
    pass

# SQLite база данных
DATABASE_URL = "sqlite:////app/data/shorturl.db"

# Создаем движок и сессии
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель базы данных
class ShortURLDB(Base):
    __tablename__ = "short_urls"

    id = Column(Integer, primary_key=True, index=True)
    short_id = Column(String, unique=True, index=True, nullable=False)
    original_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    clicks = Column(Integer, default=0)

# Создаем таблицы
Base.metadata.create_all(bind=engine)

# Pydantic модели
class ShortURLCreate(BaseModel):
    url: str

class ShortURLResponse(BaseModel):
    short_id: str
    short_url: str
    original_url: str
    created_at: datetime
    clicks: int

    class Config:
        from_attributes = True

# FastAPI приложение
app = FastAPI(
    title="URL Shortener Service API",
    description="Сервис для сокращения URL",
    version="1.0.0"
)

# Dependency для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_short_id(length: int = 6) -> str:
    """Генерация короткого идентификатора"""
    return secrets.token_urlsafe(length)[:length]

@app.post("/shorten", response_model=ShortURLResponse, status_code=201)
def create_short_url(url_data: ShortURLCreate, db: Session = Depends(get_db)):
    """Создание короткой ссылки"""
    # Генерируем уникальный short_id
    while True:
        short_id = generate_short_id()
        existing = db.query(ShortURLDB).filter(ShortURLDB.short_id == short_id).first()
        if not existing:
            break

    # Создаем запись в БД
    db_item = ShortURLDB(
        short_id=short_id,
        original_url=url_data.url
    )

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    # Формируем ответ
    return {
        "short_id": db_item.short_id,
        "short_url": f"http://localhost:8001/{db_item.short_id}",
        "original_url": db_item.original_url,
        "created_at": db_item.created_at,
        "clicks": db_item.clicks
    }

@app.get("/{short_id}")
def redirect_to_url(short_id: str, db: Session = Depends(get_db)):
    """Перенаправление по короткой ссылке"""
    url_item = db.query(ShortURLDB).filter(ShortURLDB.short_id == short_id).first()

    if url_item is None:
        raise HTTPException(status_code=404, detail="URL not found")

    # Увеличиваем счетчик кликов
    url_item.clicks += 1
    db.commit()

    return RedirectResponse(url=url_item.original_url)

@app.get("/stats/{short_id}", response_model=ShortURLResponse)
def get_url_stats(short_id: str, db: Session = Depends(get_db)):
    """Получение статистики по короткой ссылке"""
    url_item = db.query(ShortURLDB).filter(ShortURLDB.short_id == short_id).first()

    if url_item is None:
        raise HTTPException(status_code=404, detail="URL not found")

    return {
        "short_id": url_item.short_id,
        "short_url": f"http://localhost:8001/{url_item.short_id}",
        "original_url": url_item.original_url,
        "created_at": url_item.created_at,
        "clicks": url_item.clicks
    }

@app.get("/")
def read_root():
    return {"message": "URL Shortener Service is running", "docs": "/docs"}