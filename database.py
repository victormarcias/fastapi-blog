## database.py
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from config import settings

#SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./blog.db"

### DATABASE __INIT__
engine = create_async_engine(settings.database_url)

### DATABASE SESION __INIT__
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
