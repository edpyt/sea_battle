from typing import Optional

from beanie import PydanticObjectId
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import BeanieUserDatabase, ObjectIDIDMixin
from fastapi_users.exceptions import UserAlreadyExists, UserNotExists
from fastapi_users.models import UP
from fastapi_users.schemas import UC

from src.api.di.user import get_user_db
from src.infrastructure.db.models import User

SECRET = "SECRET"


class UserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(
        self, user: User, request: Optional[Request] = None
    ) -> None:
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ) -> None:
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ) -> None:
        print(
            f"Verification requested for user {user.id}."
            f"Verification token: {token}"
        )

    async def authenticate(
        self, credentials: OAuth2PasswordRequestForm
    ) -> Optional[UP]:
        """
        Authenticate and return a user following an email and a password.

        Will automatically upgrade password hash if necessary.

        :param credentials: The user credentials.
        """
        try:
            user = await User.get_by_username(credentials.username)
        except UserNotExists:
            # Run the hasher to mitigate timing attack
            # Inspired from Django: https://code.djangoproject.com/ticket/20760
            self.password_helper.hash(credentials.password)
            return None

        verified, updated_password_hash = (
            self.password_helper.verify_and_update(
                credentials.password, user.hashed_password
            )
        )
        if not verified:
            return None
        # Update password hash to a more robust one if needed
        if updated_password_hash is not None:
            await self.user_db.update(
                user, {"hashed_password": updated_password_hash}
            )

        return user

    async def create(
        self,
        user_create: UC,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> UP:
        """
        Create a user in database.

        Triggers the on_after_register handler on success.

        :param user_create: The UserCreate model to create.
        :param safe: If True, sensitive values like is_superuser or is_verified
        will be ignored during the creation, defaults to False.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises UserAlreadyExists: A user already exists with the same e-mail.
        :return: A new user.
        """
        await self.validate_password(user_create.password, user_create)

        await self._raise_if_user_already_exists(user_create)

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user

    async def _raise_if_user_already_exists(self, user_create: UC) -> None:
        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None and user_create.email is not None:
            raise UserAlreadyExists()

        existing_user = await User.get_by_username(user_create.username)
        if existing_user:
            raise UserAlreadyExists()


async def get_user_manager(user_db: BeanieUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name='jwt', transport=bearer_transport, get_strategy=get_jwt_strategy
)

fastapi_users = (
    FastAPIUsers[User, PydanticObjectId]
    (get_user_manager, [auth_backend])
)

current_active_user = fastapi_users.current_user(active=True)
