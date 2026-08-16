from sqlalchemy import select, func
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import User


async def upsert_user(session: AsyncSession, user_id: int, username: str) -> None:
    stmt = (
        insert(User)
        .values(user_id=user_id, username=username)
        .on_conflict_do_update(
            index_elements=[User.user_id],
            set_={"username": username}
        )
    )
    await session.execute(stmt)
    await session.flush()


async def get_user_count(session: AsyncSession) -> int:
    stmt = select(func.count()).select_from(User)
    result = await session.scalar(stmt)
    return result
