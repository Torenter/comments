import logging
from typing import Dict, Optional
from app.settings import settings
from jose import ExpiredSignatureError, JWTError, jwt
from pydantic import BaseModel, Field, ValidationError
from starlette.responses import Response
from typing import Optional
from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)



class UserData(BaseModel):
    """
    Данные о пользователе, которые хранятся в сессии приложения
    """

    id: int = Field(..., alias="sub")


class SessionData(BaseModel):
    user_data: UserData = Field(default_factory=UserData)


class TokenException(Exception):
    code = 1
    reason = "Unexpected"

    def __repr__(self):
        return f"{self.__class__.__name__} reason={self.reason} code={self.code}"


class TokenExpired(TokenException):
    code = 2
    reason = "Expired"


class TokenInvalidFormat(TokenException):
    code = 3
    reason = "Invalid Format"


class Token:
    @classmethod
    def decode(cls, v: str) -> Dict:
        if not v:
            return {}
        try:
            return jwt.decode(v, key=settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
        except ExpiredSignatureError:
            logger.error("jwt token expired v=%s", v)
            raise TokenInvalidFormat()
        except JWTError:
            logger.error("incorrect jwt token v=%s", v)
            raise TokenExpired()


class Session:
    """
    Класс для управления внутренней сессией пользователя
    """

    session_data_cls: SessionData = SessionData
    token = Token

    def __init__(self, data: SessionData):
        self._data = data
        # схема куки

    @property
    def is_authorized(self) -> bool:
        """
        Пользователь авторизован
        """
        return bool(self._data.user_data.id)

    @property
    def user_data(self) -> UserData:
        return self._data.user_data

    @user_data.setter
    def user_data(self, v: UserData):
        self._data.user_data = v

    @property
    def data(self) -> SessionData:
        return self._data

    @classmethod
    async def decode(cls, v: str) -> Optional["Session"]:
        try:
            return cls(
                data=cls.session_data_cls.parse_obj(cls.token.decode(v)),
            )
        except TokenException:
            # ошибка в токене <=> отсутствие токена
            return None
        except ValidationError:
            logger.error("invalid jwt token data=%s", v)
            raise

    def clear(self):
        self._data = self.session_data_cls(user_data=UserData())

    async def remove(self, response: Response):
        response.delete_cookie(key=settings.SESSION_TOKEN_KEY, domain=settings.COOKIE_DOMAIN)
        self.clear()

    @classmethod
    def create_empty(cls):
        return cls(data=cls.session_data_cls(user_data=UserData()))


DEFAULT_SESSION_CLS = Session
