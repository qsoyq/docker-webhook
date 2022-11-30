import imp
import logging

from enum import Enum
from typing import List, Optional, Union

import fastapi.applications
import fastapi.openapi.docs
import typer
import uvicorn

from fastapi import Depends, FastAPI
from fastapi_users import FastAPIUsers

from docker_webhook.api import router
from docker_webhook.database import create_db_and_tables
from docker_webhook.deps import auth_backend, cookie_backend, get_user_manager
from docker_webhook.docs import add_mermaid_support
from docker_webhook.models import User
from docker_webhook.schemas import UserCreate, UserRead, UserUpdate

fastapi.openapi.docs.get_swagger_ui_html = add_mermaid_support(fastapi.openapi.docs.get_swagger_ui_html)
fastapi.openapi.docs.get_redoc_html = add_mermaid_support(fastapi.openapi.docs.get_redoc_html)
imp.reload(fastapi.applications)

cmd = typer.Typer()
app = FastAPI()
fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend, cookie_backend])


@app.on_event("startup")
async def startup_event():
    await create_db_and_tables()


def init_fastapi_users(app: FastAPI):
    auth_tags: Optional[List[Union[str, Enum]]] = ['auth']
    auth_prefix = '/auth'
    # fastapi-users

    app.include_router(
        fastapi_users.get_auth_router(auth_backend,
                                      requires_verification=True),
        prefix=f"{auth_prefix}/jwt",
        tags=auth_tags
    )
    app.include_router(
        fastapi_users.get_auth_router(cookie_backend,
                                      requires_verification=True),
        prefix=f"{auth_prefix}/cookie",
        tags=auth_tags
    )

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
    app.include_router(router, dependencies=[Depends(fastapi_users.current_user(active=True, verified=True))])
    uvicorn.run("docker_webhook.cli.main:app", host=host, port=port, debug=debug, reload=reload)


def main():
    cmd()


if __name__ == '__main__':
    main()
