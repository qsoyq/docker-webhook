import asyncio

from typing import Optional

import typer

from pydantic.networks import EmailStr

from docker_webhook.deps import user_manager_context
from docker_webhook.schemas import UserRead, UserUpdate

cmd = typer.Typer()


@cmd.command()
def select(email: str = typer.Argument(..., help='用户邮箱地址')):
    """查询用户属性"""

    async def _select():
        async with user_manager_context() as ctx:
            user = await ctx.get_by_email(email)
            ur = UserRead.from_orm(user)
            typer.echo(f'{ur}')

    asyncio.run(_select())


@cmd.command()
def update(
    email: str = typer.Argument(...,
                                help='用户邮箱地址'),
    is_active: Optional[bool] = typer.Option(None,
                                             '--is-active/--no-is-active'),
    is_superuser: Optional[bool] = typer.Option(None,
                                                '--is-superuser/--no-is-superuser'),
    is_verified: Optional[bool] = typer.Option(None,
                                               '--is-verified/--no-is-verified'),
    password: Optional[str] = typer.Option(None,
                                           '--password'),
):
    """更新用户属性"""

    async def _update():
        async with user_manager_context() as ctx:
            user = await ctx.get_by_email(email)
            uu = UserUpdate.construct()
            if is_active is not None:
                uu.is_active = is_active
            if is_superuser is not None:
                uu.is_superuser = is_superuser
            if is_verified is not None:
                uu.is_verified = is_verified
            if password is not None:
                uu.password = password
            is_set = bool(uu.dict(exclude_none=True))
            if not is_set:
                typer.echo("未指定任何需要更新的属性")
                raise typer.Exit(-1)
            uu.email = EmailStr(email)
            typer.confirm(f"是否确认更新用户[{email}]的属性? user update: {uu.dict(exclude_none=True)}", abort=True)
            await ctx.update(uu, user)

    asyncio.run(_update())


@cmd.command()
def password_verify(email: str = typer.Argument(..., help='用户邮箱地址'), password: str = typer.Argument(..., )):
    """校验用户密码"""

    async def _password_verify():
        async with user_manager_context() as ctx:
            user = await ctx.get_by_email(email)
            is_ok, _ = ctx.password_helper.verify_and_update(password, user.hashed_password)
            if not is_ok:
                typer.echo("password incorrect")
                raise typer.Exit(-1)

    asyncio.run(_password_verify())


def main():
    cmd()


if __name__ == '__main__':
    main()
