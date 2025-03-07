from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from reviews.schemas import ReviewModel
from db.models import Book


class BookModel(BaseModel):
    id: uuid.UUID
    title: str
    author: str
    publisher:str
    published_date: datetime
    page_count: int
    language: str
    created_at : datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    update_at : datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BookDetailModel(BaseModel):
    id: uuid.UUID
    title: str
    author: str
    publisher:str
    published_date: datetime
    reviews : List[ReviewModel]


class BookCreateModel(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: datetime
    page_count: int
    language: str

class BookUpdateModel(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[datetime] = None
    page_count: Optional[int] = None
    language: Optional[str] = None