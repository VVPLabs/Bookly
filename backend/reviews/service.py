from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from db.models import Review
from auth.service import UserService
from books.service import BookService
from reviews.schemas import ReviewCreateModel
import uuid

book_service = BookService()
user_service = UserService()


class ReviewService:
    async def add_review_to_book(
        self, user_email: str, book_id: uuid.UUID, review_data: ReviewCreateModel, session: AsyncSession
    ):
        try:
            book = await book_service.get_book(book_id=book_id, session=session)
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
                )

            user = await user_service.get_user_by_email(email=user_email, session=session)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            new_review = Review(**review_data.model_dump())  # For Pydantic v1, use .dict()
            new_review.user = user
            new_review.book = book

            session.add(new_review)
            await session.commit()
            await session.refresh(new_review)  # Ensures latest DB state

            return new_review

        except HTTPException:
            raise  
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred: {str(e)}",
            )
