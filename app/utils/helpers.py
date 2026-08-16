from telegram import Update
from telegram.ext import CallbackContext
from telegram.error import TelegramError


async def delete_old_prompt(update: Update, context: CallbackContext):
    prompt_message_id = context.user_data.pop("prompt_message_id", None)
    chat_id = update.effective_chat.id

    if prompt_message_id:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=prompt_message_id)
        except TelegramError:
            pass
