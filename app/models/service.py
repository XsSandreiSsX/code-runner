from app.core.database import Base

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String


class Service(Base):
    __tablename__ = "service"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    jwt_secret: Mapped[str] = mapped_column(String(128))




