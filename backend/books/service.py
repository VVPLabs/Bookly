from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from fastapi import HTTPException, status
from .schemas import BookCreateModel, BookUpdateModel
from db.models import Book
import uuid

class BookService:
    async def get_all_books(self, session: AsyncSession):
        try:
            statement = select(Book).order_by(desc(Book.created_at))
            result = await session.exec(statement)
            books = result.all()
            return books
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch books: {str(e)}")

    async def get_book(self, book_id: uuid.UUID, session: AsyncSession):
        try:
            statement = select(Book).where(Book.id == book_id)
            result = await session.exec(statement)
            book = result.first()
            if not book:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
            return book
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch book: {str(e)}")

    async def create_book(self, book_data: BookCreateModel,user_id, session: AsyncSession):
        try:
            book_data_dict = book_data.model_dump()
            new_book = Book(**book_data_dict)
            new_book.user_id= user_id
            session.add(new_book)
            await session.commit()
            await session.refresh(new_book)
            return new_book
        except Exception as e:
            await session.rollback()  # Rollback in case of failure
            raise HTTPException(status_code=500, detail=f"Failed to create book: {str(e)}")

    async def update_book(self, book_id: uuid.UUID, update_data: BookUpdateModel, session: AsyncSession):
        try:
            book_to_update = await self.get_book(book_id, session)  
            update_data_dict = update_data.model_dump(exclude_unset=True)  

            for key, value in update_data_dict.items():
                setattr(book_to_update, key, value)

            await session.commit()
            await session.refresh(book_to_update)
            return book_to_update

        except HTTPException:
            raise  
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to update book: {str(e)}")

    async def delete_book(self, book_id: uuid.UUID, session: AsyncSession):
        try:
            book_to_delete = await self.get_book(book_id, session)  
            await session.delete(book_to_delete)
            await session.commit()
            return {"message": "Book deleted successfully"}

        except HTTPException:
            raise  
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to delete book: {str(e)}")
        

    async def get_user_books(self, user_id, session:AsyncSession):
        try:
            statement = select(Book).where(Book.user_id == user_id).order_by(desc(Book.created_at))
            result = await session.exec(statement)
            books = result.all()
            return books
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch books: {str(e)}")


