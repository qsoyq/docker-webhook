import shlex
import subprocess
import uuid

from fastapi import Body, Depends
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from runlike.inspector import Inspector
from sqlalchemy.orm import Session

import docker_webhook.crud as crud
import docker_webhook.schemas

from docker_webhook.database import get_db

router = APIRouter(prefix='/docker/webhook', tags=['docker-webhook'])


@router.get('/links', response_model=docker_webhook.schemas.Links)
def get_links(session: Session = Depends(get_db), offset: int = 0, limit: int = 100):
    links = crud.get_links(session, offset, limit)
    return {"list": links}


@router.post('/link')
def create_link(
    container: str = Body(...,
                          embed=True,
                          description='container name or container id'),
    session: Session = Depends(get_db)
):
    try:
        ins = Inspector(container, False, False)
        ins.inspect()
        ins.get_fact

        name = ins.get_fact("Name")
        assert isinstance(name, str) and '/' in name
        container_name = name.split("/")[-1]

        container_id = ins.get_fact("Id")
        assert isinstance(container_id, str)

        uid = uuid.uuid4().hex
        with session.begin():
            crud.create_link(session, container_id, container_name, uid)

    except SystemExit:
        raise HTTPException(status_code=500)

    return {"webhook": f"{uid}"}


@router.delete('/link/{uid}')
def delete_link(uid: str, session: Session = Depends(get_db)):
    with session.begin():
        crud.delete_link(session, uid)
    return {}


@router.post('/link/{uid}/run')
def runcmd(uid: str, session: Session = Depends(get_db)):
    link = crud.get_link(session, uid)

    try:
        ins = Inspector(link.container_name, False, False)
        ins.inspect()
        runcmd = ins.format_cli()
    except SystemExit:
        raise HTTPException(status_code=500)

    # todo: delete container using docker-py
    p = subprocess.run(shlex.split(str(f"docker rm -f {link.container_name}")), capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stderr)

    p = subprocess.run(shlex.split(str(runcmd)), capture_output=True, text=True)
    if p.returncode != 0:
        raise HTTPException(status_code=500, detail=p.stderr)
    return {}
