from uuid import UUID
from telegram import Update
from telegram.error import TelegramError
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from app.categories import repo, keyboards
from app.utils.wrappers import require_callback_query, require_admin, require_db_session


WAIT_NAME = 1


@require_admin
@require_callback_query
async def on_category_cancel(update: Update, context: CallbackContext, query) -> int:
    context.user_data.pop("action", None)
    context.user_data.pop("category_id", None)
    context.user_data.pop("prompt_chat_id", None)
    context.user_data.pop("prompt_message_id", None)

    await query.edit_message_text(text="Действие отменено.")
    return ConversationHandler.END


@require_admin
@require_callback_query
async def on_category_create(update: Update, context: CallbackContext, query) -> int:
    context.user_data["action"] = "create"

    msg = await query.edit_message_text(
        text="Введите имя категории:",
        reply_markup=keyboards.category_name
    )

    context.user_data["prompt_chat_id"] = msg.chat_id
    context.user_data["prompt_message_id"] = msg.message_id
    return WAIT_NAME


@require_admin
@require_callback_query
async def on_category_update(update: Update, context: CallbackContext, query) -> int:
    category_id = UUID(query.data.split(":")[-1])
    context.user_data["action"] = "update"
    context.user_data["category_id"] = category_id

    msg = await query.edit_message_text(
        text="Введите новое имя для категории:",
        reply_markup=keyboards.category_name
    )

    context.user_data["prompt_chat_id"] = msg.chat_id
    context.user_data["prompt_message_id"] = msg.message_id
    return WAIT_NAME


@require_admin
@require_db_session
async def save_category(update: Update, context: CallbackContext, session) -> int:
    action = context.user_data.pop("action", "")
    category_id = context.user_data.pop("category_id", None)
    prompt_chat_id = context.user_data.pop("prompt_chat_id", None)
    prompt_message_id = context.user_data.pop("prompt_message_id", None)

    exists = await repo.get_category_by_name(session=session, name=update.message.text)
    if exists:
        await update.message.reply_text("Категория с таким именем уже существует.")

    elif action == "create":
        await repo.create_category(session=session, name=update.message.text)
        await update.message.reply_text("Категория успешно создана.")

    elif action == "update" and category_id:
        await repo.update_category(session=session, category_id=category_id, new_name=update.message.text)
        await update.message.reply_text("Категория успешно обновлена.")

    if prompt_chat_id and prompt_message_id:
        try:
            await context.bot.delete_message(chat_id=prompt_chat_id, message_id=prompt_message_id)
        except TelegramError: pass

    return ConversationHandler.END


category_manage_conv = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(on_category_create, pattern="^categories:create$"),
        CallbackQueryHandler(on_category_update, pattern="^categories:update:[0-9a-fA-F-]+$")
    ],
    states={
        WAIT_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, save_category)
        ],
    },
    fallbacks=[CallbackQueryHandler(on_category_cancel, pattern="^categories:cancel$")],
)

