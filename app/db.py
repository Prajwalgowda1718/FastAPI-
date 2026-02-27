import uuid
from datetime import datetime
from contextlib import asynccontextmanager
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.orm import relationship
import uuid
from fastapi import Depends

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

Base =declarative_base()

class User(SQLAlchemyBaseUserTableUUID, Base):
    posts = relationship("Post", back_populates="user")

class Post(Base):
    __tablename__ = "posts"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    caption    = Column(Text)
    url        = Column(String, nullable=False)
    file_type  = Column(String, nullable=False)
    file_name  = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id    = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    user       = relationship("User", back_populates="posts")


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def create_db_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session():
    async with async_session_maker() as session:
        yield session

# Dependency to get user DB
async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)