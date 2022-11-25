from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from docker_webhook.database import async_session_maker
from docker_webhook.models import User, get_user_db

USER_SECRET = "SECRET"
expires_in = 3600 * 24 * 2

auth_transport = BearerTransport(tokenUrl='auth/jwt/login')


def get_strategy() -> JWTStrategy:
    return JWTStrategy(secret=USER_SECRET, lifetime_seconds=expires_in)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=auth_transport,
    get_strategy=get_strategy,
)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = USER_SECRET
    verification_token_secret = USER_SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


@asynccontextmanager
async def user_manager_context() -> AsyncGenerator[UserManager, None]:
    async with async_session_maker() as session:  # type: ignore
        user_db = SQLAlchemyUserDatabase(session, User)
        yield UserManager(user_db)
