from uuid import UUID
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext
from app.files import repo, keyboards, messages
from app.categories import repo as category_repo
from app.utils.wrappers import require_admin, require_callback_query, require_db_session


@require_admin
@require_callback_query
async def on_files_admin_menu(update: Update, context: CallbackContext, query) -> None:
    await query.edit_message_text(
        text="Выберите действие ниже.",
        reply_markup=keyboards.file_admin_menu
    )


@require_admin
@require_callback_query
@require_db_session
async def on_file_admin_categories(update: Update, context: CallbackContext, query, session) -> None:
    categories = await category_repo.get_categories(session=session)
    if not categories:
        await query.edit_message_text(text="Файловых категорий не найдено.")
        return

    await query.edit_message_text(
        text="Выберите категорию файлов, которые хотите увидеть",
        reply_markup=keyboards.file_admin_categories(categories=categories)
    )


@require_admin
@require_callback_query
@require_db_session
async def on_files_admin_page(update: Update, context: CallbackContext, query, session) -> None:
    offset = int(query.data.split(":")[-2])
    category_id = UUID(query.data.split(":")[-1])
    file_count = await repo.get_file_count_by_category(session=session, category_id=category_id)
    if not file_count:
        await query.edit_message_text(text="Файлов не найдено.")
        return

    offset = offset % file_count
    file = await repo.get_file_by_category(session=session, offset=offset, category_id=category_id)

    try:
        await query.edit_message_text(
            text=messages.file(
                file_name=file.file_name,
                file_type=file.file_type,
                byte_size=file.byte_size,
                created_at=file.created_at
            ),
            reply_markup=keyboards.files_admin_paging(offset=offset, count=file_count, file_id=file.id, category_id=category_id)
        )
    except BadRequest as exc:
        if "Message is not modified" not in str(exc):
            raise


@require_callback_query
@require_db_session
async def on_files_page(update: Update, context: CallbackContext, query, session) -> None:
    offset = int(query.data.split(":")[-2])
    category_id = UUID(query.data.split(":")[-1])
    file_count = await repo.get_file_count_by_category(session=session, category_id=category_id)
    if not file_count:
        await query.edit_message_text(text="Файлов не найдено.")
        return

    offset = offset % file_count
    file = await repo.get_file_by_category(session=session, offset=offset, category_id=category_id)

    try:
        await query.edit_message_text(
            text=messages.file(
                file_name=file.file_name,
                file_type=file.file_type,
                byte_size=file.byte_size,
                created_at=file.created_at
            ),
            reply_markup=keyboards.files_paging(offset=offset, count=file_count, file_id=file.id, category_id=category_id)
        )
    except BadRequest as exc:
        if "Message is not modified" not in str(exc):
            raise


@require_callback_query
@require_db_session
async def on_file_categories(update: Update, context: CallbackContext, query, session) -> None:
    categories = await category_repo.get_categories(session=session)
    if not categories:
        await query.edit_message_text(text="Файловых категорий не найдено.")
        return

    await query.edit_message_text(
        text="Выберите категорию файлов, которые хотите увидеть",
        reply_markup=keyboards.file_categories(categories=categories)
    )


@require_callback_query
@require_db_session
async def on_file_download(update: Update, context: CallbackContext, query, session) -> None:
    file_id = UUID(query.data.split(":")[-1])
    chat_id = update.effective_chat.id

    file = await repo.get_file_by_id(session=session, file_id=file_id)
    if not file:
        await query.edit_message_text(text="Файл не найден.")
        return

    if file.file_type == "document":
        await context.bot.send_document(chat_id=chat_id, document=file.file_id)

    elif file.file_type == "photo":
        await context.bot.send_photo(chat_id=chat_id, photo=file.file_id)

    elif file.file_type == "video":
        await context.bot.send_video(chat_id=chat_id, video=file.file_id)

    elif file.file_type == "video_note":
        await context.bot.send_video_note(chat_id=chat_id, video_note=file.file_id)

    elif file.file_type == "voice":
        await context.bot.send_voice(chat_id=chat_id, voice=file.file_id)

    elif file.file_type == "audio":
        await context.bot.send_audio(chat_id=chat_id, audio=file.file_id)

    await query.edit_message_text(text="Ваш файл выгружен к вам в личный чат.")


@require_admin
@require_callback_query
@require_db_session
async def on_file_delete(update: Update, context: CallbackContext, query, session) -> None:
    file_id = UUID(query.data.split(":")[-1])
    await repo.delete_file(session=session, file_id=file_id)
    await query.edit_message_text(text="Файл удален.")
