from app.core.database import Base
from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, ForeignKey



class TestCase(Base):
    __tablename__ = "testcase"

    id: Mapped[int] = mapped_column(primary_key=True)
    stdout: Mapped[str] = mapped_column(Text)

    test_suite_id: Mapped[int] = mapped_column(ForeignKey("testsuite.id"))
    test_suite: Mapped["TestSuite"] = relationship(back_populates="test_cases")


class TestSuite(Base):
    __tablename__ = "testsuite"

    id: Mapped[int] = mapped_column(primary_key=True)

    time_limit: Mapped[int] = mapped_column()
    memory_limit: Mapped[int] = mapped_column()

    test_cases: Mapped[List["TestCase"]] = relationship(
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    service_id: Mapped[int] = mapped_column(ForeignKey("service.id"))
    service: Mapped["Service"] = relationship(back_populates="test_suites")

