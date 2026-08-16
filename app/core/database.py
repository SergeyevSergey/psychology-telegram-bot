import uuid
from datetime import datetime, timezone
from sqlalchemy import Uuid, String, DateTime, ForeignKey, Integer, BigInteger, Boolean, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


engine = create_async_engine("sqlite+aiosqlite:///database.db", echo=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase): pass


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    feedbacks: Mapped[list["Feedback"]] = relationship(back_populates="user", lazy="noload")
    poll_responses: Mapped[list["PollResponse"]] = relationship(back_populates="user", lazy="noload", passive_deletes=True)


class FileCategory(Base):
    __tablename__ = "file_categories"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    files: Mapped[list["File"]] = relationship(back_populates="category", lazy="noload")


class File(Base):
    __tablename__ = "files"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    file_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    file_name: Mapped[str] = mapped_column(String, nullable=False)
    file_type: Mapped[str] = mapped_column(String, nullable=False)
    byte_size: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("file_categories.id", ondelete="RESTRICT"), nullable=False)
    category: Mapped["FileCategory"] = relationship(back_populates="files", lazy="joined")


class Feedback(Base):
    __tablename__ = "feedbacks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    text: Mapped[str] = mapped_column(String, nullable=False)
    mode: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    chat_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    message_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    user: Mapped["User"] = relationship(back_populates="feedbacks", lazy="joined")


class Poll(Base):
    __tablename__ = "polls"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    allows_multiple_answers: Mapped[bool] = mapped_column(Boolean, nullable=False)
    mode: Mapped[str] = mapped_column(String, nullable=False)
    is_anonymous: Mapped[bool] = mapped_column(Boolean, nullable=False)
    correct_option_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    options: Mapped[list["PollOption"]] = relationship(back_populates="poll", lazy="noload", passive_deletes=True)


class PollOption(Base):
    __tablename__ = "poll_options"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    text: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    poll_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("polls.id", ondelete="CASCADE"), nullable=False)
    poll: Mapped["Poll"] = relationship(back_populates="options", lazy="noload")
    responses: Mapped[list["PollResponse"]] = relationship(back_populates="option", lazy="noload", passive_deletes=True)


class PollResponse(Base):
    __tablename__ = "poll_responses"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    option_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("poll_options.id", ondelete="CASCADE"), nullable=False)
    option: Mapped["PollOption"] = relationship(back_populates="responses", lazy="noload")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    poll_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user: Mapped["User"] = relationship(back_populates="poll_responses", lazy="noload")



async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
