import json
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.settings import settings


def dumps(val):
    return json.dumps(val, default=str)


sql_url = "{0}+asyncpg:{1}:{2}:{3}".format(*settings.DB_URL.split(":"))

sunc_engine = create_engine(settings.DB_URL, json_serializer=dumps)
engine = create_async_engine(sql_url, json_serializer=dumps)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=True, autocommit=False, autoflush=True)
