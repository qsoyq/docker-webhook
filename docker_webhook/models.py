from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession

from docker_webhook.database import Base, get_async_session


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True)
    container_name = Column(String, unique=True, index=True)
    container_id = Column(String, unique=True, index=True)
    uid = Column(String, unique=True, index=True)


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)  # type: ignore


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
