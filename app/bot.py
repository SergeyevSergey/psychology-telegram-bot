import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

from app.feedbacks.handlers import callbacks as feedback_callbacks
from app.feedbacks.handlers import convs as feedback_conversations

from app.categories.handlers import callbacks as category_callbacks
from app.categories.handlers import convs as category_conversations

from app.polls.handlers import callbacks as poll_callbacks
from app.polls.handlers import convs as poll_conversations

from app.files.handlers import callbacks as file_callbacks
from app.files.handlers import convs as file_conversations

from app.core.database import init_db
from app.common.commands import start, menu, admin
from app.common.callbacks import on_about, on_stats


load_dotenv()
TOKEN = os.environ.get("BOT_TOKEN")
logger = logging.getLogger(__name__)


def main():
    try:
        asyncio.run(init_db())

        # Application
        app = (
            ApplicationBuilder()
            .token(TOKEN)
            .get_updates_connect_timeout(10)
            .get_updates_read_timeout(20)
            .get_updates_write_timeout(20)
            .get_updates_pool_timeout(5)
            .build()
        )

        # Command handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("menu", menu))
        app.add_handler(CommandHandler("admin", admin))

        # Conversation handlers
        app.add_handler(feedback_conversations.feedback_manage_conv)
        app.add_handler(category_conversations.category_manage_conv)
        app.add_handler(poll_conversations.poll_create_conv)
        app.add_handler(file_conversations.file_create_conv)

        # Callback handlers
        app.add_handler(CallbackQueryHandler(on_about, pattern="^about$"))
        app.add_handler(CallbackQueryHandler(on_stats, pattern="^stats$"))

        app.add_handler(CallbackQueryHandler(feedback_callbacks.on_feedbacks_page, pattern="^feedbacks:page:\d+$"))
        app.add_handler(CallbackQueryHandler(feedback_callbacks.on_feedback_delete, pattern="^feedbacks:delete:[0-9a-fA-F-]+$"))

        app.add_handler(CallbackQueryHandler(category_callbacks.on_categories_admin_menu, pattern="^categories:admin_menu$"))
        app.add_handler(CallbackQueryHandler(category_callbacks.on_categories_page, pattern="^categories:page:\d+$"))
        app.add_handler(CallbackQueryHandler(category_callbacks.on_category_delete, pattern="^categories:delete:[0-9a-fA-F-]+$"))

        app.add_handler(CallbackQueryHandler(poll_callbacks.on_polls_admin_menu, pattern="^polls:admin_menu$"))
        app.add_handler(CallbackQueryHandler(poll_callbacks.on_polls_admin_page, pattern="^polls:admin_page:\d+$"))
        app.add_handler(CallbackQueryHandler(poll_callbacks.on_polls_page, pattern="^polls:page:\d+$"))
        app.add_handler(CallbackQueryHandler(poll_callbacks.on_poll_options, pattern="^polls:options:[0-9a-fA-F-]+$"))
        app.add_handler(CallbackQueryHandler(poll_callbacks.on_poll_delete, pattern="^polls:delete:[0-9a-fA-F-]+$"))
        app.add_handler(CallbackQueryHandler(poll_callbacks.on_poll_stats, pattern="^polls:stats:[0-9a-fA-F-]+$"))
        app.add_handler(CallbackQueryHandler(poll_callbacks.on_poll_vote, pattern="^polls:vote:[0-9a-fA-F-]+$"))
        app.add_handler(CallbackQueryHandler(poll_callbacks.on_poll_retract, pattern="^polls:retract:[0-9a-fA-F-]+$"))

        app.add_handler(CallbackQueryHandler(file_callbacks.on_files_admin_menu, pattern="^files:admin_menu$"))
        app.add_handler(CallbackQueryHandler(file_callbacks.on_file_admin_categories, pattern="^files:admin_categories$"))
        app.add_handler(CallbackQueryHandler(file_callbacks.on_files_admin_page, pattern="^files:admin_page:\d+:[0-9a-fA-F-]+$"))
        app.add_handler(CallbackQueryHandler(file_callbacks.on_file_categories, pattern="^files:categories$"))
        app.add_handler(CallbackQueryHandler(file_callbacks.on_files_page, pattern="^files:page:\d+:[0-9a-fA-F-]+$"))
        app.add_handler(CallbackQueryHandler(file_callbacks.on_file_download, pattern="^files:download:[0-9a-fA-F-]+$"))
        app.add_handler(CallbackQueryHandler(file_callbacks.on_file_delete, pattern="^files:delete:[0-9a-fA-F-]+$"))

        # Polling
        app.run_polling()
    except Exception:
        logger.error("Application startup failed", exc_info=True)


if __name__ == "__main__":
    main()
