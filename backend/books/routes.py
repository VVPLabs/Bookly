from fastapi import APIRouter, status, Depends, Response
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import BookModel, BookUpdateModel, BookCreateModel, BookDetailModel
from db.main import get_session
from books.service import BookService
from db.models import Book
from auth.dependecies import AccessTokenBearer, RoleChecker
import uuid

book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker_admin = RoleChecker(['admin'])
role_checker_user =RoleChecker(['admin', 'user'])

@book_router.get("/", response_model=list[BookModel])
async def list_books(
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer),
    _:bool= Depends(role_checker_user)
):
    return await book_service.get_all_books(session)


@book_router.get("/user/{user_id}", response_model=list[BookModel])
async def get_user_book(
    user_id,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer),
    _:bool= Depends(role_checker_user)
):
    return await book_service.get_user_books(user_id , session )



@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book)
async def create_books(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer),
    _:bool= Depends(role_checker_user)
):
    user_id = token_details.get('user')['user_uid']
    return await book_service.create_book(book_data,user_id, session)







@book_router.get("/{book_id}", response_model=BookDetailModel)
async def get_book(
    book_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer),
    _:bool= Depends(role_checker_user)
):
    book = await book_service.get_book(book_id, session)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book Not Found 😥😥"
        )
    return book


@book_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer),
    _:bool= Depends(role_checker_admin)
):
    deleted = await book_service.delete_book(book_id, session)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book Not Found 😥😥"
        )
    return Response(content="Book deleted successfully", status_code=status.HTTP_204_NO_CONTENT)


@book_router.patch("/{book_id}", response_model=BookDetailModel)
async def update_book(
    book_id: uuid.UUID,
    book_update_data: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer),
    _:bool= Depends(role_checker_user)
):
    updated_book = await book_service.update_book(book_id, book_update_data, session)
    if not updated_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book Not Found 😥"
        )
    return updated_book
