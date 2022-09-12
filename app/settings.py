from typing import List
from pydantic import BaseSettings


class AuthSettings(BaseSettings):
    JWT_SECRET_KEY: str = "Aaa111Bbb"
    JWT_ALGORITHM: str = "HS256"
    SESSION_TOKEN_KEY: str = "comments_session"
    COOKIE_DOMAIN: str = ".sso_service"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Settings(AuthSettings, BaseSettings):
    ENVIRONMENT: str = "qa"
    SERVICE_NAME = "Comments"
    DB_URL: str
    PORT: int = 8000
    ACCESS_LOG: bool = True
    DEBUG: bool = False
    FILTER_HEALTH_CHECK_LOG: bool = True
    HEALTH_CHECK_PATH: str = "/srv/ping"
    METRICS_SKIP_PATH: List[str] = ["/srv/ping"]  # Пути по которым не будут собираться метрики

    #: Sentry. Оставить пустым, если не используется
    SENTRY_DSN: str = ""

    #: CORS
    CORS_ORIGIN_REGEX = ""
    CORS_ORIGIN_REGEX_QA = ""

    def cross_origin_regex(self):
        if self.ENVIRONMENT == "qa":
            return self.CORS_ORIGIN_REGEX_QA
        return self.CORS_ORIGIN_REGEX


settings = Settings()
