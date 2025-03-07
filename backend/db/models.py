from datetime import date, datetime, timezone
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import Column
from typing import Optional, List
import uuid


def remove_timezone(dt: datetime) -> datetime:
   
    return dt.replace(tzinfo=None) if dt.tzinfo else dt


class User(SQLModel, table=True):
    id: uuid.UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    )
    username: str
    email: EmailStr
    first_name: Optional[str] = Field(default=None, nullable=True)
    last_name: Optional[str] = Field(default=None, nullable=True)
    role: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="user"))
    is_verified: Optional[bool] = Field(default=False)
    password_hash: str = Field(exclude=True)
    created_at : datetime = Field(default_factory=lambda: remove_timezone(datetime.now(timezone.utc)))
    updated_at: datetime = Field(default_factory=lambda: remove_timezone(datetime.now(timezone.utc)))

    books: List["Book"] = Relationship(back_populates="user", sa_relationship_kwargs={'lazy': 'selectin', 'cascade': 'all, delete-orphan'} )
    reviews: List["Review"] = Relationship(back_populates="user", sa_relationship_kwargs={'lazy': 'selectin', 'cascade': 'all, delete-orphan'})

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class Book(SQLModel, table=True):
    id: uuid.UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    )
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")
    created_at : datetime = Field(default_factory=lambda: remove_timezone(datetime.now(timezone.utc)))
    updated_at: datetime = Field(default_factory=lambda: remove_timezone(datetime.now(timezone.utc)))
    user: Optional["User"] = Relationship(back_populates="books", sa_relationship_kwargs={"lazy": "joined"})
    reviews: List["Review"] = Relationship(back_populates="book", sa_relationship_kwargs={'lazy': 'selectin', 'cascade': 'all, delete-orphan'})

    def __repr__(self):
        return f"<Book {self.title}>"


class Review(SQLModel, table=True):
    id: uuid.UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    )
    rating: int = Field(ge=1, le=5)  # Ensures a 1-5 range
    review_text: str
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")
    book_id: Optional[uuid.UUID] = Field(default=None, foreign_key="book.id")
    created_at : datetime = Field(default_factory=lambda: remove_timezone(datetime.now(timezone.utc)))
    updated_at: datetime = Field(default_factory=lambda: remove_timezone(datetime.now(timezone.utc)))
    user: Optional["User"] = Relationship(back_populates="reviews", sa_relationship_kwargs={"lazy": "joined"})
    book: Optional["Book"] = Relationship(back_populates="reviews", sa_relationship_kwargs={"lazy": "joined"})

    def __repr__(self):
        return f"<Review {self.review_text}>"
