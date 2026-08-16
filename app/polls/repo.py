from uuid import UUID, uuid4
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import Poll, PollOption, PollResponse


async def create_poll(
        session: AsyncSession,
        title: str,
        allows_multiple_answers: bool,
        mode: str,
        is_anonymous: bool,
        options: list[str],
        correct_option: str = None
) -> None:
    poll = Poll(
        title=title,
        allows_multiple_answers=allows_multiple_answers,
        mode=mode,
        is_anonymous=is_anonymous,
        options=[PollOption(id=uuid4(), text=opt, position=pos) for pos, opt in enumerate(options)]
    )

    if mode == "quiz" and correct_option:
        correct_opt = next((option for option in poll.options if option.text == correct_option), None)
        if correct_opt:
            poll.correct_option_id = correct_opt.id

    session.add(poll)
    await session.flush()


async def get_poll(session: AsyncSession, offset: int) -> Poll:
    stmt = select(Poll).order_by(Poll.title.desc()).limit(1).offset(offset)
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_poll_by_id(session: AsyncSession, poll_id: UUID) -> Poll | None:
    stmt = select(Poll).where(Poll.id == poll_id)
    result = await session.execute(stmt)
    return result.scalars().one_or_none()


async def get_poll_by_option_id(session: AsyncSession, option_id: UUID) -> Poll | None:
    stmt = (
        select(Poll)
        .join(Poll.options)
        .where(PollOption.id == option_id)
    )
    poll = await session.scalar(stmt)
    return poll


async def get_poll_count(session: AsyncSession) -> int:
    stmt = select(func.count()).select_from(Poll)
    result = await session.scalar(stmt)
    return result


async def get_poll_voters_count(session: AsyncSession, poll_id: UUID) -> int:
    stmt = (
        select(func.count(func.distinct(PollResponse.user_id)))
        .where(PollResponse.poll_id == poll_id)
    )
    result = await session.scalar(stmt) or 0
    return result


async def get_poll_options(session: AsyncSession, poll_id: UUID) -> list["PollOption"]:
    stmt = select(PollOption).where(PollOption.poll_id == poll_id).order_by(PollOption.position.asc())
    result = (await session.scalars(stmt)).all()
    return list(result)


async def get_poll_options_vote_count(session: AsyncSession, poll_id: UUID) -> list[tuple[PollOption, int]]:
    stmt = (
        select(PollOption, func.count(PollResponse.id))
        .outerjoin(PollResponse, PollOption.id == PollResponse.option_id)
        .where(PollOption.poll_id == poll_id)
        .group_by(PollOption.id)
        .order_by(PollOption.position.asc())
    )
    result = await session.execute(stmt)
    return [(option, count) for option, count in result.all()]


async def delete_poll(session: AsyncSession, poll_id: UUID) -> None:
    stmt = delete(Poll).where(Poll.id == poll_id)
    await session.execute(stmt)


async def get_user_votes_for_poll(session: AsyncSession, poll_id: UUID, user_id: int) -> set[UUID]:
    stmt = select(PollResponse.option_id).where(
        PollResponse.poll_id == poll_id,
        PollResponse.user_id == user_id
    )
    result = await session.scalars(stmt)
    return set(result.all())


async def verify_poll_voted(session: AsyncSession, poll_id: UUID, user_id: int) -> bool:
    stmt = select(PollResponse).where(PollResponse.user_id == user_id, PollResponse.poll_id == poll_id)
    result = await session.execute(stmt)
    return result.scalar() is not None


async def create_poll_response(session: AsyncSession, option_id: UUID, poll_id: UUID, user_id: int) -> None:
    response = PollResponse(
        option_id=option_id,
        poll_id=poll_id,
        user_id=user_id
    )
    session.add(response)
    await session.flush()


async def delete_poll_responses_by_user(session: AsyncSession, poll_id: UUID, user_id: int) -> None:
    stmt = delete(PollResponse).where(PollResponse.poll_id == poll_id, PollResponse.user_id == user_id)
    await session.execute(stmt)
    await session.flush()
