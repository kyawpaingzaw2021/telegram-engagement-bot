from datetime import datetime
from sqlalchemy import (
    BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text, func
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)

    api_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    api_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    view_count: Mapped[int] = mapped_column(Integer, default=20)
    react_count: Mapped[int] = mapped_column(Integer, default=10)
    ads_count: Mapped[int] = mapped_column(Integer, default=5)
    delay_minutes: Mapped[int] = mapped_column(Integer, default=5)

    timer_on: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    services: Mapped["Service"] = relationship(back_populates="user", uselist=False)
    sessions: Mapped[list["Session"]] = relationship(back_populates="user")
    target: Mapped["Target"] = relationship(back_populates="user", uselist=False)
    channels: Mapped[list["TargetChannel"]] = relationship(back_populates="user")


class Service(Base):
    __tablename__ = "services"

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), primary_key=True
    )
    worker_on: Mapped[bool] = mapped_column(Boolean, default=True)
    scheduler_on: Mapped[bool] = mapped_column(Boolean, default=True)
    ads_on: Mapped[bool] = mapped_column(Boolean, default=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="services")


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), index=True
    )

    label: Mapped[str] = mapped_column(String(64))
    phone: Mapped[str] = mapped_column(String(32))
    session_string: Mapped[str] = mapped_column(Text)

    status: Mapped[str] = mapped_column(String(16), default="active")
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="sessions")
    logs: Mapped[list["Log"]] = relationship(back_populates="session")


class Target(Base):
    __tablename__ = "targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), unique=True
    )

    target_bot: Mapped[str | None] = mapped_column(String(128), nullable=True)
    ads_channel: Mapped[str | None] = mapped_column(String(128), nullable=True)

    user: Mapped["User"] = relationship(back_populates="target")


class TargetChannel(Base):
    __tablename__ = "target_channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), index=True
    )

    channel_username: Mapped[str] = mapped_column(String(128))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="channels")


class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sessions.id", ondelete="CASCADE"), index=True
    )

    task_type: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16))
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    ran_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    session: Mapped["Session"] = relationship(back_populates="logs")
