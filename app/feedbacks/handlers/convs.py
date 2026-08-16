from telegram import Update
from telegram.error import TelegramError
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from app.feedbacks import repo, keyboards
from app.utils.wrappers import require_callback_query, require_db_session


CHOOSE_MODE = 1
WAIT_TEXT = 2


@require_callback_query
async def on_feedback_create(update: Update, context: CallbackContext, query) -> int:
    await query.edit_message_text(
        text="Вы можете отправить сообщение администратору.\n\n"
        "Выберите режим:",
        reply_markup=keyboards.feedback_mode
    )
    return CHOOSE_MODE


@require_callback_query
async def on_feedback_mode(update: Update, context: CallbackContext, query) -> int:
    context.user_data["mode"] = query.data.split(":")[-1]
    msg = await query.edit_message_text(
        text="Напишите сообщение:",
        reply_markup=keyboards.feedback_message
    )

    context.user_data["prompt_chat_id"] = msg.chat_id
    context.user_data["prompt_message_id"] = msg.message_id
    return WAIT_TEXT


@require_db_session
async def save_feedback(update: Update, context: CallbackContext, session) -> int:
    mode = context.user_data.pop("mode", "feedback_anonymous")
    prompt_chat_id = context.user_data.pop("prompt_chat_id", None)
    prompt_message_id = context.user_data.pop("prompt_message_id", None)
    
    chat_id = update.effective_chat.id if mode == "feedback_normal" else None
    message_id = update.effective_message.message_id if mode == "feedback_normal" else None
    user_id = update.effective_user.id if mode == "feedback_normal" else None

    await repo.create_feedback(
        session=session,
        mode=mode,
        chat_id=chat_id,
        message_id=message_id,
        user_id=user_id,
        text=update.message.text,
    )
    
    if prompt_chat_id and prompt_message_id:
        try:
            await context.bot.delete_message(chat_id=prompt_chat_id, message_id=prompt_message_id)
        except TelegramError: pass
    
    await update.message.reply_text(text="Сообщение отправлено.")
    return ConversationHandler.END


@require_callback_query
async def on_feedback_cancel(update: Update, context: CallbackContext, query) -> int:
    context.user_data.pop("mode", None)
    context.user_data.pop("prompt_chat_id", None)
    context.user_data.pop("prompt_message_id", None)
    
    await query.edit_message_text(text="Действие отменено.")
    return ConversationHandler.END


feedback_manage_conv = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(on_feedback_create, pattern="^feedbacks:create$"),
    ],
    states={
        CHOOSE_MODE: [
            CallbackQueryHandler(on_feedback_mode, pattern="^feedbacks:mode:(normal|anonymous)$")
        ],
        WAIT_TEXT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, save_feedback)
        ],
    },
    fallbacks=[CallbackQueryHandler(on_feedback_cancel, pattern="^feedbacks:cancel$")],
)
