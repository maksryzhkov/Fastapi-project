from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, Field
from typing import Optional, List
import os

# SQLite база данных
DATABASE_URL = "sqlite:////app/data/todo.db"

# Создаем движок и сессии
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель базы данных
class ToDoItemDB(Base):
    __tablename__ = "todo_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)

# Pydantic модели
class ToDoItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class ToDoItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class ToDoItemResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool

    class Config:
        from_attributes = True

# FastAPI приложение
app = FastAPI(
    title="ToDo Service API",
    description="Сервис для управления задачами",
    version="1.0.0"
)

# Создаем таблицы при запуске (если их нет)
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

# Dependency для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/items", response_model=ToDoItemResponse, status_code=201)
def create_item(item: ToDoItemCreate, db: Session = Depends(get_db)):
    """Создание новой задачи"""
    db_item = ToDoItemDB(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items", response_model=List[ToDoItemResponse])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получение списка всех задач"""
    items = db.query(ToDoItemDB).offset(skip).limit(limit).all()
    return items

@app.get("/items/{item_id}", response_model=ToDoItemResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
    """Получение задачи по ID"""
    item = db.query(ToDoItemDB).filter(ToDoItemDB.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.put("/items/{item_id}", response_model=ToDoItemResponse)
def update_item(item_id: int, item_update: ToDoItemUpdate, db: Session = Depends(get_db)):
    """Обновление задачи по ID"""
    db_item = db.query(ToDoItemDB).filter(ToDoItemDB.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)

    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Удаление задачи по ID"""
    db_item = db.query(ToDoItemDB).filter(ToDoItemDB.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(db_item)
    db.commit()
    return None

@app.get("/")
def root():
    return {"message": "ToDo Service is running", "docs": "/docs"}