from app.core.database import Base
from app.core.app_exceptions import UnknownFieldError, NoFilterError
from app.core.http_exceptions import ConflictError

from app.models.service import Service

from typing import Generic, TypeVar, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import inspect, delete, select

T = TypeVar("T", bound=Base)

class BaseDAO(Generic[T]):
    model: Type[T]
    FORBIDDEN_FIELDS = {"id", "created_at", "updated_at"}
    ALLOWED_FIELDS: set[str] = set()
    ALLOWED_RELATIONSHIPS: set[str] = set()

    @classmethod
    async def get_or_none(cls, session: AsyncSession, **filters) -> T | None:
        if not filters:
            raise NoFilterError("Filters cannot be empty")

        stmt = select(cls.model)
        for k, v in filters.items():
            stmt = stmt.where(getattr(cls.model, k) == v)

        res = await session.execute(stmt)
        return res.scalar_one_or_none()


    @classmethod
    async def add(cls, session: AsyncSession, data: dict) -> T:
        await cls._check_model_fields(data)

        new_obj = cls.model(**data)
        session.add(new_obj)

        try:
            await session.flush()
        except IntegrityError:
            raise ConflictError(f"This obj in {cls.model.__tablename__} already exists")

        return new_obj

    @classmethod
    async def update_obj(cls, session: AsyncSession, data: dict, *, obj: T) -> T:
        await cls._check_model_fields(data)
        for k, v in data.items():
            setattr(obj, k, v)

        await session.flush()
        return obj

    @classmethod
    async def delete_many(cls, session: AsyncSession, **filters) -> None:
        if not filters:
            raise NoFilterError("Filters cannot be empty")
        await cls._check_model_fields(filters)
        stmt = delete(cls.model)

        for k, v in filters.items():
            col = getattr(cls.model, k)
            if isinstance(v, (list, tuple, set)):
                stmt = stmt.where(col.in_(list(v)))
            else:
                stmt = stmt.where(col == v)

        await session.execute(stmt)
        await session.flush()

    @classmethod
    async def delete_obj(cls, session: AsyncSession, *, obj: T) -> None:
        await session.delete(obj)
        await session.flush()


    @classmethod
    async def _check_model_fields(cls, data: dict) -> None:
        unknown = set(data.keys()) - cls.ALLOWED_FIELDS
        fields = ", ".join([f for f in unknown])
        if unknown:
            raise UnknownFieldError(f"Unknown fields: [{fields}] in {cls.model.__tablename__}")

    @classmethod
    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if cls.model is None:
            return

        mapper = inspect(cls.model).mapper
        cols = {c.key for c in mapper.column_attrs}
        rels = set(mapper.relationships.keys())

        cls.ALLOWED_FIELDS.update((cols | (rels & cls.ALLOWED_RELATIONSHIPS)) - cls.FORBIDDEN_FIELDS)

class ServiceDAO(BaseDAO[Service]):
    model = Service
