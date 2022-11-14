import logging

import typer
import uvicorn

from fastapi import FastAPI

from docker_webhook.api import router
from docker_webhook.database import Base, engine

cmd = typer.Typer()
app = FastAPI()


@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(engine)


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
    app.include_router(router)
    uvicorn.run("docker_webhook.main:app", host=host, port=port, debug=debug, reload=reload)


def main():
    cmd()


if __name__ == '__main__':
    main()
