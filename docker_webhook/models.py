from sqlalchemy import Column, Integer, String

from docker_webhook.database import Base


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    container_name = Column(String, unique=True, index=True)
    container_id = Column(String, unique=True, index=True)
    uid = Column(String, unique=True, index=True)
