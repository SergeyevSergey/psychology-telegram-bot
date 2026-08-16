from uuid import UUID
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import Feedback


async def create_feedback(session: AsyncSession, chat_id: int, message_id: int | None, user_id: int | None, mode: str, text: str) -> None:
    feedback = Feedback(
        chat_id=chat_id,
        message_id=message_id,
        user_id=user_id,
        text=text,
        mode=mode
    )
    session.add(feedback)
    await session.flush()


async def get_feedback(session: AsyncSession, offset: int) -> Feedback:
    stmt = select(Feedback).order_by(Feedback.created_at.desc()).limit(1).offset(offset)
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_feedback_count(session: AsyncSession) -> int:
    stmt = select(func.count()).select_from(Feedback)
    result = await session.scalar(stmt)
    return result


async def delete_feedback(session: AsyncSession, feedback_id: UUID) -> None:
    stmt = delete(Feedback).where(Feedback.id == feedback_id)
    await session.execute(stmt)
