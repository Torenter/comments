import asyncio
from urllib.parse import urlparse

import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from jose import jwt

import alembic.config
from app.application import app as _app
from app.settings import settings
from database.database import async_session
from datetime import datetime, timedelta
from database.tables import Users
from app.api.v1.auth.models import pwd_context


def pytest_collection_modifyitems(items):
    """
    Позволяет не добавляться @pytest.mark.asyncio
    к асинхронным тестам
    """
    for item in items:
        item.add_marker("asyncio")


@pytest.fixture
def non_mocked_hosts() -> list:
    """Сервисы, к которым будет уходить прямой запрос"""
    return ["test"]


@pytest.fixture(scope="function", autouse=True)
async def app():
    async with LifespanManager(_app):
        yield _app


@pytest.fixture
def assert_all_responses_were_requested():
    return False


@pytest.fixture(autouse=True)
def _http_mock(httpx_mock):
    """
    Обязательно мокаем все запросы к сторонним сервисам
    """


@pytest.fixture
async def client(app) -> AsyncClient:
    """
    Выполняет запуск приложения для каждого теста и возвращает асинхронный клиент для взаимодействия с ним
    LifespanManager позволяет корректно выполнить запуск и остановку приложения
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        data = {"user_data":{"sub": 1, "expire": (datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).isoformat()}}
        token = jwt.encode(data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        ac.headers[settings.SESSION_TOKEN_KEY] = token
        ac.cookies[settings.SESSION_TOKEN_KEY] = token

        yield ac


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    """Вспомогательная функция"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def session():
    """асинхронная DB сессия"""
    async with async_session() as session:
        yield session


@pytest.fixture()
async def create_user(session):
    a = Users(name="test", login="test", password_hash=pwd_context.hash("123aaa"))
    session.add(a)
    await session.commit()
    yield


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    """
    Фикстура для очистки данных в БД и накатки миграций между запусками тестов
    """
    db_host = urlparse(settings.DB_URL).hostname
    assert db_host in ("localhost", "pg", "0.0.0.0", "new_admin_db")

    # Удаление всех таблиц из БД
    alembic.config.main(argv=["downgrade", "base"])
    # Накатка миграций
    alembic.config.main(argv=["upgrade", "head"])
