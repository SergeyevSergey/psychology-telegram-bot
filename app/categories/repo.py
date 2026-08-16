from uuid import UUID
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import File, FileCategory


async def create_category(session: AsyncSession, name: str) -> None:
    category = FileCategory(name=name)
    session.add(category)
    await session.flush()


async def get_category(session: AsyncSession, offset: int) -> FileCategory:
    stmt = select(FileCategory).order_by(FileCategory.name.desc()).limit(1).offset(offset)
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_categories(session: AsyncSession) -> list[FileCategory]:
    stmt = select(FileCategory)
    result = (await session.scalars(stmt)).all()
    return list(result)


async def get_category_by_name(session: AsyncSession, name: str) -> FileCategory | None:
    stmt = select(FileCategory).where(FileCategory.name == name)
    result = await session.execute(stmt)
    return result.scalars().one_or_none()


async def get_category_count(session: AsyncSession) -> int:
    stmt = select(func.count()).select_from(FileCategory)
    result = await session.scalar(stmt)
    return result


async def get_category_files_count(session: AsyncSession, category_id: UUID) -> int:
    stmt = select(func.count()).select_from(File).where(File.category_id == category_id)
    result = await session.scalar(stmt)
    return result


async def update_category(session: AsyncSession, category_id: UUID, new_name: str) -> None:
    stmt = update(FileCategory).where(FileCategory.id == category_id).values(**{"name": new_name})
    await session.execute(stmt)


async def delete_category(session: AsyncSession, category_id: UUID) -> None:
    stmt = delete(FileCategory).where(FileCategory.id == category_id)
    await session.execute(stmt)
