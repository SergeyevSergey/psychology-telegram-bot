from uuid import UUID
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from app.files import repo, keyboards
from app.categories import repo as category_repo
from app.utils.wrappers import require_admin, require_callback_query, require_db_session
from app.utils.helpers import delete_old_prompt


CHOOSE_CATEGORY = 1
WAIT_NAME = 2
WAIT_FILE = 3


@require_admin
@require_callback_query
async def on_file_cancel(update: Update, context: CallbackContext, query) -> int:
    context.user_data.pop("draft_file", {})
    context.user_data.pop("prompt_message_id", None)

    await query.edit_message_text(text="Действие отменено.")
    return ConversationHandler.END


@require_admin
@require_callback_query
@require_db_session
async def on_file_create(update: Update, context: CallbackContext, query, session) -> int:
    categories = await category_repo.get_categories(session=session)
    if not categories:
        await query.edit_message_text(text="Файловых категорий не найдено.")
        return ConversationHandler.END

    context.user_data["draft_file"] = {}

    await query.edit_message_text(
        text="Выберите файловую категорию:",
        reply_markup=keyboards.file_category(categories=categories)
    )
    return CHOOSE_CATEGORY


@require_admin
@require_callback_query
async def on_file_category(update: Update, context: CallbackContext, query) -> int:
    category_id = UUID(query.data.split(":")[-1])
    context.user_data["draft_file"]["category_id"] = category_id

    msg = await query.edit_message_text(
        text="Введите имя файла:",
        reply_markup=keyboards.file_message
    )
    context.user_data["prompt_message_id"] = msg.message_id
    return WAIT_NAME


@require_admin
async def on_file_name(update: Update, context: CallbackContext) -> int:
    context.user_data["draft_file"]["file_name"] = update.message.text

    msg = await update.message.reply_text(
        text="Загрузите файл:",
        reply_markup=keyboards.file_message
    )

    await delete_old_prompt(update=update, context=context)
    context.user_data["prompt_message_id"] = msg.message_id
    return WAIT_FILE


@require_admin
@require_db_session
async def save_file(update: Update, context: CallbackContext, session) -> int:
    msg = update.message
    data = context.user_data.pop("draft_file")
    category_id = data.get("category_id")
    file_name = data.get("file_name")
    file_id = None
    file_size = 0
    file_type = "document"

    if msg.document:
        file_id = msg.document.file_id
        file_size = msg.document.file_size
        file_type = "document"

    elif msg.photo:
        file_id = msg.photo[-1].file_id
        file_size = msg.photo[-1].file_size
        file_type = "photo"

    elif msg.video:
        file_id = msg.video.file_id
        file_size = msg.video.file_size
        file_type = "video"

    elif msg.video_note:
        file_id = msg.video_note.file_id
        file_size = msg.video_note.file_size
        file_type = "video_note"

    elif msg.voice:
        file_id = msg.voice.file_id
        file_size = msg.voice.file_size
        file_type = "voice"

    elif msg.audio:
        file_id = msg.audio.file_id
        file_size = msg.audio.file_size
        file_type = "audio"

    await repo.create_file(
        session=session,
        file_id=file_id,
        file_name=file_name,
        file_type=file_type,
        byte_size=file_size,
        category_id=category_id
    )

    await delete_old_prompt(update=update, context=context)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Файл успешно загружен."
    )
    return ConversationHandler.END


file_create_conv = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(on_file_create, pattern="^files:create$"),
    ],
    states={
        CHOOSE_CATEGORY: [
            CallbackQueryHandler(on_file_category, pattern="^files:category:[0-9a-fA-F-]+$")
        ],
        WAIT_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, on_file_name)
        ],
        WAIT_FILE: [
            MessageHandler(
                (
                    filters.Document.ALL
                    | filters.PHOTO
                    | filters.VIDEO
                    | filters.AUDIO
                    | filters.VOICE
                    | filters.VIDEO_NOTE
                ),
                save_file
            )
        ],
    },
    fallbacks=[
        CallbackQueryHandler(on_file_cancel, pattern="^files:cancel$"),
    ],
)
