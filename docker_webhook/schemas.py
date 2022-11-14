from typing import List

from pydantic import BaseModel


class Link(BaseModel):
    container_name: str
    container_id: str
    uid: str

    class Config:
        orm_mode = True


class Links(BaseModel):
    list: List[Link]
