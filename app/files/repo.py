from uuid import UUID
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import File


async def create_file(session: AsyncSession, file_id: str, file_name: str, file_type: str, byte_size: int, category_id: UUID) -> None:
    file = File(file_id=file_id, file_name=file_name, file_type=file_type, byte_size=byte_size, category_id=category_id)
    session.add(file)
    await session.flush()


async def get_file_by_id(session: AsyncSession, file_id: UUID) -> File | None:
    stmt = select(File).where(File.id == file_id)
    result = await session.execute(stmt)
    return result.scalars().one_or_none()


async def get_file_by_category(session: AsyncSession, offset: int, category_id: UUID) -> File:
    stmt = select(File).where(File.category_id == category_id).order_by(File.file_name.desc()).limit(1).offset(offset)
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_file_count(session: AsyncSession) -> int:
    stmt = select(func.count()).select_from(File)
    result = await session.scalar(stmt)
    return result


async def get_file_count_by_category(session: AsyncSession, category_id: UUID) -> int:
    stmt = select(func.count()).select_from(File).where(File.category_id == category_id)
    result = await session.scalar(stmt)
    return result


async def delete_file(session: AsyncSession, file_id: UUID) -> None:
    stmt = delete(File).where(File.id == file_id)
    await session.execute(stmt)
