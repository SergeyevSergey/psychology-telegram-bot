from uuid import UUID
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext
from app.polls import repo, keyboards, messages
from app.utils.wrappers import require_admin, require_callback_query, require_db_session


@require_admin
@require_callback_query
async def on_polls_admin_menu(update: Update, context: CallbackContext, query) -> None:
    await query.edit_message_text(
        text="Выберите действие ниже.",
        reply_markup=keyboards.poll_admin_menu
    )


@require_admin
@require_callback_query
@require_db_session
async def on_polls_admin_page(update: Update, context: CallbackContext, query, session) -> None:
    offset = int(query.data.split(":")[-1])
    poll_count = await repo.get_poll_count(session=session)
    if not poll_count:
        await query.edit_message_text(text="Опросов не найдено.")
        return

    offset = offset % poll_count
    poll = await repo.get_poll(session=session, offset=offset)
    options = await repo.get_poll_options(session=session, poll_id=poll.id)

    try:
        await query.edit_message_text(
            text=messages.poll_admin(poll=poll, options=options),
            reply_markup=keyboards.poll_admin_paging(offset=offset, count=poll_count, poll_id=poll.id)
        )
    except BadRequest as exc:
        if "Message is not modified" not in str(exc):
            raise


@require_admin
@require_callback_query
@require_db_session
async def on_poll_stats(update: Update, context: CallbackContext, query, session) -> None:
    poll_id = UUID(query.data.split(":")[-1])

    total_voters = await repo.get_poll_voters_count(session=session, poll_id=poll_id)
    options_votes = await repo.get_poll_options_vote_count(session=session, poll_id=poll_id)

    await query.edit_message_text(
        text=messages.poll_stats(options_votes=options_votes, total_voters=total_voters)
    )


@require_callback_query
@require_db_session
async def on_polls_page(update: Update, context: CallbackContext, query, session) -> None:
    offset = int(query.data.split(":")[-1])
    poll_count = await repo.get_poll_count(session=session)
    if not poll_count:
        await query.edit_message_text(text="Опросов не найдено.")
        return

    offset = offset % poll_count
    poll = await repo.get_poll(session=session, offset=offset)
    voted = await repo.verify_poll_voted(session=session, poll_id=poll.id, user_id=update.effective_user.id)

    try:
        await query.edit_message_text(
            text=messages.poll(poll=poll),
            reply_markup=keyboards.poll_paging(offset=offset, count=poll_count, poll_id=poll.id, voted=voted)
        )
    except BadRequest as exc:
        if "Message is not modified" not in str(exc):
            raise


@require_callback_query
@require_db_session
async def on_poll_options(update: Update, context: CallbackContext, query, session) -> None:
    poll_id = UUID(query.data.split(":")[-1])
    user_id = update.effective_user.id

    poll = await repo.get_poll_by_id(session=session, poll_id=poll_id)
    if not poll:
        await query.edit_message_text(text="Опрос не найден.")
        return

    user_votes = await repo.get_user_votes_for_poll(session=session, poll_id=poll_id, user_id=user_id)
    total_voters = await repo.get_poll_voters_count(session=session, poll_id=poll_id)
    options_votes = await repo.get_poll_options_vote_count(session=session, poll_id=poll_id)

    await query.edit_message_text(
        text=f"Тема опроса: {poll.title}",
        reply_markup=keyboards.poll_options(
            option_votes=options_votes,
            user_votes=user_votes,
            total_voters=total_voters,
            poll=poll
        )
    )


@require_db_session
@require_callback_query
async def on_poll_vote(update: Update, context: CallbackContext, query, session):
    option_id = UUID(query.data.split(":")[-1])
    user_id = update.effective_user.id

    poll = await repo.get_poll_by_option_id(session=session, option_id=option_id)
    if not poll:
        await query.edit_message_text(text="Опрос не найден.")
        return
    
    user_votes = await repo.get_user_votes_for_poll(session, poll.id, user_id)
    has_voted = len(user_votes) > 0

    if poll.mode == "quiz":
        if has_voted:
            await query.answer("В викторине можно отвечать только один раз.", show_alert=True)
            return
        else:
            await repo.create_poll_response(session=session, user_id=user_id, poll_id=poll.id, option_id=option_id)
            if option_id == poll.correct_option_id:
                await query.answer("Правильно! 🎉", show_alert=True)
            else:
                await query.answer("Увы, это неправильный ответ ❌", show_alert=True)

    elif poll.mode == "poll" and not poll.allows_multiple_answers:
        if has_voted:
            await query.answer("Вы уже голосовали.", show_alert=True)
            return
        else:
            await repo.create_poll_response(session=session, user_id=user_id, poll_id=poll.id, option_id=option_id)
            await query.answer("Голос учтен!")

    elif poll.mode == "poll" and poll.allows_multiple_answers:
        if option_id in user_votes:
            await query.answer("Вы уже голосовали за этот вариант.", show_alert=True)
            return
        else:
            await repo.create_poll_response(session=session, user_id=user_id, poll_id=poll.id, option_id=option_id)
            await query.answer("Выбор добавлен")

    user_votes = await repo.get_user_votes_for_poll(session=session, poll_id=poll.id, user_id=user_id)
    total_voters = await repo.get_poll_voters_count(session=session, poll_id=poll.id)
    options_votes = await repo.get_poll_options_vote_count(session=session, poll_id=poll.id)

    await query.edit_message_text(
        text=f"Тема опроса: {poll.title}",
        reply_markup=keyboards.poll_options(
            option_votes=options_votes,
            user_votes=user_votes,
            total_voters=total_voters,
            poll=poll
        )
    )


@require_callback_query
@require_db_session
async def on_poll_retract(update: Update, context: CallbackContext, query, session) -> None:
    poll_id = UUID(query.data.split(":")[-1])
    user_id = update.effective_user.id

    poll = await repo.get_poll_by_id(session=session, poll_id=poll_id)
    if not poll:
        await query.edit_message_text(text="Опрос не найден.")
        return

    await repo.delete_poll_responses_by_user(session=session, poll_id=poll_id, user_id=user_id)

    user_votes = await repo.get_user_votes_for_poll(session=session, poll_id=poll.id, user_id=user_id)
    total_voters = await repo.get_poll_voters_count(session=session, poll_id=poll.id)
    options_votes = await repo.get_poll_options_vote_count(session=session, poll_id=poll.id)

    await query.edit_message_text(
        text=f"Тема опроса: {poll.title}",
        reply_markup=keyboards.poll_options(
            option_votes=options_votes,
            user_votes=user_votes,
            total_voters=total_voters,
            poll=poll
        )
    )


@require_admin
@require_callback_query
@require_db_session
async def on_poll_delete(update: Update, context: CallbackContext, query, session) -> None:
    poll_id = UUID(query.data.split(":")[-1])
    await repo.delete_poll(session=session, poll_id=poll_id)
    await query.edit_message_text(text="Опрос удален.")
