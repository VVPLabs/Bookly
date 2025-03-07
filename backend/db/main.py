from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import Config
from db.models import Book

#  Create the async engine
async_engine = create_async_engine(
    Config.DATABASE_URL,
)

#  Initialize database and create tables
async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

#  Create the async session maker 
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,  
    expire_on_commit=False
)

#  Correct session dependency function
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session  #  Ensures session is closed properly after use
