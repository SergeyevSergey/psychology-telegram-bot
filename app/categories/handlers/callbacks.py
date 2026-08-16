from uuid import UUID
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext
from app.categories import repo, messages, keyboards
from app.utils.wrappers import require_callback_query, require_admin, require_db_session


@require_admin
@require_callback_query
async def on_categories_admin_menu(update: Update, context: CallbackContext, query) -> None:
    await query.edit_message_text(
        text="Выберите действие ниже.",
        reply_markup=keyboards.category_admin_menu
    )


@require_admin
@require_callback_query
@require_db_session
async def on_categories_page(update: Update, context: CallbackContext, query, session) -> None:
    offset = int(query.data.split(":")[-1])
    category_count = await repo.get_category_count(session=session)
    if not category_count:
        await query.edit_message_text(text="Категорий не найдено.")
        return

    offset = offset % category_count
    category = await repo.get_category(session=session, offset=offset)
    category_file_count = await repo.get_category_files_count(session=session, category_id=category.id)

    try:
        await query.edit_message_text(
            text=messages.category(
                name=category.name,
                file_count=category_file_count
            ),
            reply_markup=keyboards.categories_paging(
                offset=offset,
                count=category_count,
                category_id=category.id
            )
        )
    except BadRequest as exc:
        if "Message is not modified" not in str(exc):
            raise


@require_admin
@require_callback_query
@require_db_session
async def on_category_delete(update: Update, context: CallbackContext, query, session) -> None:
    category_id = UUID(query.data.split(":")[-1])
    category_file_count = await repo.get_category_files_count(session=session, category_id=category_id)
    if category_file_count:
        await query.edit_message_text(text=f"Невозможно удалить категорию пока она содержит хотя бы один файл.")
        return

    await repo.delete_category(session=session, category_id=category_id)
    await query.edit_message_text(text="Категория удалена.")
