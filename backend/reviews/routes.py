import uuid
from fastapi import APIRouter, Depends
from db.models import User
from reviews.schemas import ReviewCreateModel
from db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession 
from reviews.service import ReviewService
from auth.dependecies import get_current_user

review_router = APIRouter()
review_service = ReviewService()

@review_router.post('/book/{book_id}')
async def add_review_to_book(
    book_id: uuid.UUID, 
    review_data : ReviewCreateModel, 
    current_user:User= Depends(get_current_user), 
    session :AsyncSession= Depends(get_session) ):


    new_review = await review_service.add_review_to_book(
        user_email=current_user.email,
        review_data= review_data,
        book_id= book_id,
        session= session,
    )

    return new_review
