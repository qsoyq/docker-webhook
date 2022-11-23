import logging

from enum import Enum
from typing import List, Optional, Union

import typer
import uvicorn

from fastapi import FastAPI
from fastapi_users import FastAPIUsers

from docker_webhook.api import router
from docker_webhook.database import create_db_and_tables
from docker_webhook.deps import auth_backend, get_user_manager
from docker_webhook.models import User
from docker_webhook.schemas import UserCreate, UserRead, UserUpdate

cmd = typer.Typer()
app = FastAPI()


@app.on_event("startup")
async def startup_event():
    await create_db_and_tables()


def init_fastapi_users(app: FastAPI):
    auth_tags: Optional[List[Union[str, Enum]]] = ['auth']
    auth_prefix = '/auth'
    # fastapi-users
    fastapi_users = FastAPIUsers[User,
                                 int](
                                     get_user_manager,
                                     [auth_backend],
                                 )
    app.include_router(fastapi_users.get_auth_router(auth_backend), prefix=f"{auth_prefix}/jwt", tags=auth_tags)

    app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix=auth_prefix, tags=auth_tags)

    app.include_router(fastapi_users.get_verify_router(UserRead), prefix=auth_prefix, tags=auth_tags)

    app.include_router(fastapi_users.get_reset_password_router(), prefix=auth_prefix, tags=auth_tags)

    app.include_router(
        fastapi_users.get_users_router(UserRead,
                                       UserUpdate),
        prefix="/users",
        tags=["users"],
    )


@cmd.command()
def http(
    host: str = typer.Option("0.0.0.0",
                             '--host',
                             '-h',
                             envvar='http_host'),
    port: int = typer.Option(8000,
                             '--port',
                             '-p',
                             envvar='http_port'),
    debug: bool = typer.Option(False,
                               '--debug',
                               envvar='http_debug'),
    reload: bool = typer.Option(False,
                                '--debug',
                                envvar='http_reload'),
    log_level: int = typer.Option(logging.DEBUG,
                                  '--log_level',
                                  envvar='log_level'),
    name: str = typer.Option("",
                             '--name'),
):
    """启动 http 服务"""
    logging.basicConfig(level=log_level)
    logging.info(f"http server listening on {host}:{port}")
    init_fastapi_users(app)
    app.include_router(router)
    uvicorn.run("docker_webhook.main:app", host=host, port=port, debug=debug, reload=reload)


def main():
    cmd()


if __name__ == '__main__':
    main()
