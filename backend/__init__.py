
from contextlib import asynccontextmanager
from fastapi import FastAPI
from books.routes import book_router
from db.main import init_db
from auth.routes import auth_router
from reviews.routes import review_router
from middleware import register_middleware




version= "v1"

app = FastAPI(
    title="Bookly",
    description="A REST api",
    version= version,
)

register_middleware(app)

app.include_router(book_router, prefix=f"/api/{version}/books" , tags=["Books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["Auth"])
app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=["Reviews"])