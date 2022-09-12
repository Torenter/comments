from contextvars import ContextVar

from fastapi import Depends, HTTPException, Request
from fastapi.security import APIKeyHeader
from jose import jwt
from starlette import status
from .auth_dependency import SessionTokenDependency, cookie_sec
from .session import UserData

from app.settings import settings

CUR_AUTH_DATA = ContextVar("cur_auth_data")


class AuthToken:
    async def __call__(
        self,
        request: Request,
        header=Depends(APIKeyHeader(name=settings.SESSION_TOKEN_KEY, auto_error=False)),
        cookie=Depends(cookie_sec),
    ) -> UserData:
        token = header or cookie
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        session = await SessionTokenDependency()(token)
        if not session.is_authorized:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        CUR_AUTH_DATA.set(session.user_data)
        request.state.user_data = session.user_data
        return CUR_AUTH_DATA.get()

    @classmethod
    def create_token(cls, *, data=None):
        if data is None:
            data = {}

        return jwt.encode(data, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
