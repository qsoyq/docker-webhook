from typing import List

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from pydantic import BaseModel


class Link(BaseModel):
    container_name: str
    container_id: str
    uid: str

    class Config:
        orm_mode = True


class Links(BaseModel):
    list: List[Link]


class UserRead(BaseUser[int]):
    pass


class UserCreate(BaseUserCreate):
    pass


class UserUpdate(BaseUserUpdate):
    pass
