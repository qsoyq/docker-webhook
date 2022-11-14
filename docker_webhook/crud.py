from typing import List

from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session

from docker_webhook.models import Link


def get_links(session: Session, offset: int = 0, limit: int = 100) -> List[Link]:
    stmt = select(Link).offset(offset).limit(limit)
    return session.execute(stmt).scalars().all()


def get_link(session: Session, uid: str) -> Link:
    stmt = select(Link).where(Link.uid == uid)
    return session.execute(stmt).scalar_one()


def create_link(session: Session, container_id: str, container_name: str, uid: str):
    stmt = insert(Link).values(**{"container_name": container_name, "container_id": container_id, "uid": uid})
    return session.execute(stmt)


def delete_link(session: Session, uid: str):
    stmt = delete(Link).where(Link.uid == uid)
    return session.execute(stmt)
