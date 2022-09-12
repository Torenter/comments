import logging
from typing import Optional, Type

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyCookie
from pydantic import ValidationError
from starlette import status

from .session import DEFAULT_SESSION_CLS, Session
from app.settings import settings

logger = logging.getLogger(__name__)

cookie_sec = APIKeyCookie(name=settings.SESSION_TOKEN_KEY, auto_error=False)


class SessionTokenDependency:
    """
    Организует работу с сессией пользователя через Token
    """

    def __init__(self, session_cls: Type[Session] = DEFAULT_SESSION_CLS):
        self.session_cls = session_cls

    async def __call__(self, v: Optional[str] = Depends(cookie_sec)) -> Session:
        # токен должен быть
        if not v:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        try:
            session = await self.session_cls.decode(v)
        except ValidationError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token data")

        if not session:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        return session
