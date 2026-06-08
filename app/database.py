import logging
from typing import Generic, Type, TypeVar

from sqlalchemy import delete, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.app_exceptions import NoFilterError, UnknownFieldError
from app.core.database import Base
from app.core.http_exceptions import ConflictError
from app.models import Service, Submission, TestSuite

T = TypeVar("T", bound=Base)


logger = logging.getLogger(__name__)


class BaseDAO(Generic[T]):
    """DAO layer for database access.

    Provides a safe async interface for working with SQLAlchemy models, including
    CRUD operations, field validation, dynamic filters, and common database error
    handling.
    """

    model: Type[T]
    FORBIDDEN_FIELDS = {"id", "created_at", "updated_at"}
    ALLOWED_FIELDS: set[str] = set()

    @classmethod
    async def get_one_or_none(cls, session: AsyncSession, **filters) -> T | None:
        """Get one object by filters or return None."""
        if not filters:
            raise NoFilterError("Filters cannot be empty")

        logger.debug(
            "Fetching one object: table=%s filter_fields=%s",
            cls.model.__tablename__,
            list(filters.keys()),
        )

        stmt = select(cls.model)
        stmt = cls._apply_filters(stmt, filters)

        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    @classmethod
    async def get_many_or_none(cls, session: AsyncSession, **filters) -> list[T] | None:
        """Get many objects by filters or return an empty list."""
        if not filters:
            raise NoFilterError("Filters cannot be empty")

        logger.debug(
            "Fetching many objects: table=%s filter_fields=%s",
            cls.model.__tablename__,
            list(filters.keys()),
        )

        stmt = select(cls.model)
        stmt = cls._apply_filters(stmt, filters)

        res = await session.execute(stmt)
        objects = res.scalars().all()

        return list(objects)

    @classmethod
    async def add(cls, session: AsyncSession, data: dict) -> T:
        """Create a new model object from validated data."""
        await cls._check_model_fields(data)

        logger.debug(
            "Creating object: table=%s fields=%s",
            cls.model.__tablename__,
            list(data.keys()),
        )

        new_obj = cls.model(**data)
        session.add(new_obj)

        try:
            await session.flush()
        except IntegrityError:
            raise ConflictError(f"This obj in {cls.model.__tablename__} already exists")

        return new_obj

    @classmethod
    async def update_obj(cls, session: AsyncSession, data: dict, *, obj: T) -> T:
        """Update an existing model object with validated data."""
        await cls._check_model_fields(data)

        logger.debug(
            "Updating object: table=%s fields=%s",
            cls.model.__tablename__,
            list(data.keys()),
        )

        for k, v in data.items():
            setattr(obj, k, v)

        await session.flush()
        return obj

    @classmethod
    async def delete_many(cls, session: AsyncSession, **filters) -> None:
        """Delete many objects matching the given filters."""
        if not filters:
            raise NoFilterError("Filters cannot be empty")

        await cls._check_model_fields(filters)

        logger.debug(
            "Deleting many objects: table=%s filter_fields=%s",
            cls.model.__tablename__,
            list(filters.keys()),
        )

        stmt = delete(cls.model)
        stmt = cls._apply_filters(stmt, filters)

        await session.execute(stmt)
        await session.flush()

    @classmethod
    async def delete_obj(cls, session: AsyncSession, *, obj: T) -> None:
        """Delete a specific model object."""
        logger.debug(
            "Deleting object: table=%s",
            cls.model.__tablename__,
        )

        await session.delete(obj)
        await session.flush()

    @classmethod
    async def _check_model_fields(cls, data: dict) -> None:
        """Validate that all fields are allowed for the model."""
        unknown = set(data.keys()) - cls.ALLOWED_FIELDS
        fields = ", ".join([f for f in unknown])

        if unknown:
            raise UnknownFieldError(
                f"Unknown fields: [{fields}] in {cls.model.__tablename__}"
            )

    @classmethod
    def _apply_filters(cls, stmt, filters: dict):
        """Apply equality or IN filters to a SQLAlchemy statement."""
        for k, v in filters.items():
            col = getattr(cls.model, k)

            if isinstance(v, (list, tuple, set)):
                stmt = stmt.where(col.in_(list(v)))
            else:
                stmt = stmt.where(col == v)

        return stmt

    @classmethod
    def __init_subclass__(cls, **kwargs) -> None:
        """Collect allowed model fields for each DAO subclass."""
        super().__init_subclass__(**kwargs)

        if cls.model is None:
            return

        mapper = inspect(cls.model).mapper
        cols = {c.key for c in mapper.column_attrs}
        rels = set(mapper.relationships.keys())

        cls.ALLOWED_FIELDS = (cols | rels) - cls.FORBIDDEN_FIELDS


class ServiceDAO(BaseDAO[Service]):
    model = Service


class TestSuiteDAO(BaseDAO[TestSuite]):
    model = TestSuite


class SubmissionDAO(BaseDAO[Submission]):
    model = Submission