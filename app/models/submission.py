from app.core.database import Base
from shared.models.enums import SubmissionStatus, SubmissionVerdict

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum, ForeignKey


class Submission(Base):
    __tablename__ = "submission"

    id: Mapped[int] = mapped_column(primary_key=True)
    celery_task_id: Mapped[str | None] = mapped_column(nullable=True)
    status: Mapped[SubmissionStatus] = mapped_column(Enum(SubmissionStatus),
                                                     default=SubmissionStatus.IN_QUEUE)
    verdict: Mapped[SubmissionVerdict | None] = mapped_column(Enum(SubmissionVerdict),
                                                              nullable=True)

    source_code: Mapped[str] = mapped_column()
    testsuite_id: Mapped[int] = mapped_column(ForeignKey("testsuite.id"))
    testsuite: Mapped["TestSuite"] = relationship()

    failed_test_index: Mapped[int | None] = mapped_column(nullable=True)
    error_message: Mapped[str | None] = mapped_column(nullable=True)
    time_used: Mapped[int | None] = mapped_column(nullable=True)
    memory_used: Mapped[int | None] = mapped_column(nullable=True)
    tests_passed: Mapped[int | None] = mapped_column(nullable=True)

    service_id: Mapped[int] = mapped_column(ForeignKey("service.id"))
    service: Mapped["Service"] = relationship(back_populates="submissions"

    )