from app.core.database import Base
from app.models.test_suite import TestSuite
from app.models.submission import Submission

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from typing import List



class Service(Base):
    __tablename__ = "service"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    jwt_secret: Mapped[str] = mapped_column(String(128))

    test_suites: Mapped[List["TestSuite"]] = relationship(
        cascade="all, delete-orphan",
    )

    submissions: Mapped[List["Submission"]] = relationship(
        cascade="all, delete-orphan",
    )