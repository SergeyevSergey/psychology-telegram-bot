from telegram import Update
from telegram.ext import CallbackContext

from app.users.repo import get_user_count
from app.files.repo import get_file_count
from app.polls.repo import get_poll_count
from app.categories.repo import get_category_count
from app.feedbacks.repo import get_feedback_count

from app.common import texts, messages
from app.utils.wrappers import require_callback_query, require_db_session, require_admin


@require_callback_query
async def on_about(update: Update, context: CallbackContext, query) -> None:
    await query.edit_message_text(text=texts.ABOUT)


@require_admin
@require_callback_query
@require_db_session
async def on_stats(update: Update, context: CallbackContext, query, session) -> None:
    user_count = await get_user_count(session=session)
    file_count = await get_file_count(session=session)
    poll_count = await get_poll_count(session=session)
    category_count = await get_category_count(session=session)
    feedback_count = await get_feedback_count(session=session)

    await query.edit_message_text(
        text=messages.stats(
            user_count=user_count,
            feedback_count=feedback_count,
            category_count=category_count,
            file_count=file_count,
            poll_count=poll_count
        )
    )


