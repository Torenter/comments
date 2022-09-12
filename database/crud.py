from datetime import datetime
from typing import Dict, List, Tuple, Union

from sqlalchemy import delete, select, literal_column
from sqlalchemy import update as sql_update


class BaseCrud:
    @classmethod
    async def delete(cls, session, obj: List) -> None:
        """
        Удалить строки/строку
        Принимает любые модели проекта
        Args:
            obj List[Models]: модель Sqlalchemy.
        """
        for el in obj:
            await session.delete(el)
        return

    @classmethod
    async def delete_by_field(cls, session, fields: Dict) -> None:
        """Удалит все строки, что имеют значение fields

        Args:
            fields Dict[str:Any]: {'колонка':значение}.
        """
        await session.execute(delete(cls).where(*[getattr(cls, key) == value for key, value in fields.items()]))
        return

    @classmethod
    async def get(cls, session, id_: Union[int, Tuple[int]] = None, fields: dict = None) -> list:
        """Возвращает строку/строки

        WARNING:
            Или Id_ или Fields

        Args:
            id_ (int, tuple): [уникальный id строки в БД]. Defaults to None.
            fields (dict, optional): [колонка:значение]. Defaults to None.

        Returns:
            при любом запросе вернет список моделей
        """
        if all([not id_, not fields]):
            raise ValueError
        if id_:
            if isinstance(id_, int):
                obj = await session.get(cls, id_)
                return [obj]
            if isinstance(id_, tuple):
                result = await session.execute(select(cls).where(cls.id.in_(id_)))
                return result.scalars().all()

        result = await session.execute(select(cls).where(*[getattr(cls, k) == v for k, v in fields.items()]))

        return result.scalars().all()

    @classmethod
    async def get_by_field_in_json(cls, session, field, filed_in_json, value) -> list:

        query = select(cls).filter(cls.field[filed_in_json].astext in value)
        result = await session.execue(query)
        return result.scalars().all()

    @classmethod
    async def insert(cls, session, fields: List[Dict]) -> None:
        """Производит единичную/множественную вставку

        Args:
            fields (List[Dict[str:Any]]): [{'колонка':значение},...].
        """
        for model in fields:
            session.add(
                cls(
                    **model,
                )
            )
        return

    @classmethod
    async def update(cls, session, id_: int, **kwargs):
        """Производит обновление строки по ее ИД
        kwargs - произвольный набор колонок и новых значений
        """
        query = sql_update(cls).where(cls.id == id_).values(**kwargs).returning(literal_column("*"))
        return await session.execute(query)
