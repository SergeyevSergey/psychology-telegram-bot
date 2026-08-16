from uuid import UUID
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext
from app.feedbacks import keyboards, messages, repo
from app.utils.wrappers import require_callback_query, require_db_session, require_admin


@require_admin
@require_callback_query
@require_db_session
async def on_feedbacks_page(update: Update, context: CallbackContext, query, session) -> None:
    offset = int(query.data.split(":")[-1])
    feedback_count = await repo.get_feedback_count(session=session)
    if not feedback_count:
        await query.edit_message_text(text="Сообщений не найдено.")
        return

    offset = offset % feedback_count
    feedback = await repo.get_feedback(session=session, offset=offset)

    try:
        await query.edit_message_text(
            text=messages.feedback(
                username=feedback.user.username if feedback.user else None,
                text=feedback.text,
                created_at=feedback.created_at
            ),
            reply_markup=keyboards.feedback_paging(
                offset=offset,
                count=feedback_count,
                feedback_id=feedback.id
            )
        )
    except BadRequest as exc:
        if "Message is not modified" not in str(exc):
            raise


@require_admin
@require_callback_query
@require_db_session
async def on_feedback_delete(update: Update, context: CallbackContext, query, session) -> None:
    feedback_id = UUID(query.data.split(":")[-1])
    await repo.delete_feedback(session=session, feedback_id=feedback_id)
    await query.edit_message_text(text="Сообщение удалено.")
