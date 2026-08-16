from telegram import Update
from telegram.ext import CallbackContext
from app.common import keyboards, texts
from app.users.repo import upsert_user
from app.utils.wrappers import require_db_session, require_admin


@require_db_session
async def start(update: Update, context: CallbackContext, session) -> None:
    await upsert_user(
        session=session,
        user_id=update.effective_user.id,
        username=update.effective_user.username
    )
    await update.message.reply_text(
        text=texts.START,
        reply_markup=keyboards.main_menu
    )


async def menu(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        text=texts.MENU,
        reply_markup=keyboards.main_menu
    )


@require_admin
async def admin(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        text=texts.ADMIN_PANEL,
        reply_markup=keyboards.admin_menu
    )
