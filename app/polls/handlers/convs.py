from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from app.polls import repo, keyboards
from app.utils.wrappers import require_admin, require_callback_query, require_db_session
from app.utils.helpers import delete_old_prompt


CHOOSE_MODE = 1
CHOOSE_ANONYMOUS_MODE = 2
CHOOSE_ANSWER_MODE = 3
WAIT_TITLE = 4
WAIT_OPTIONS = 5
CHOOSE_CORRECT_OPTION = 6


@require_admin
@require_callback_query
async def on_poll_cancel(update: Update, context: CallbackContext, query) -> int:
    context.user_data.pop("draft_poll", {})
    context.user_data.pop("prompt_message_id", None)

    await query.edit_message_text(text="Действие отменено.")
    return ConversationHandler.END


@require_admin
@require_callback_query
async def on_poll_create(update: Update, context: CallbackContext, query) -> int:
    context.user_data["draft_poll"] = {}

    await query.edit_message_text(
        text="Выберите режим опроса:",
        reply_markup=keyboards.poll_mode
    )
    return CHOOSE_MODE


@require_admin
@require_callback_query
async def on_poll_mode(update: Update, context: CallbackContext, query) -> int:
    mode = query.data.split(":")[-1]
    context.user_data["draft_poll"]["mode"] = mode

    if mode == "poll":
        await query.edit_message_text(
            text="Выберите каким будет опрос:",
            reply_markup=keyboards.poll_anon_mode
        )
        return CHOOSE_ANONYMOUS_MODE

    else:
        msg = await query.edit_message_text(
            text="Введите тему викторины:",
            reply_markup=keyboards.poll_message
        )
        context.user_data["prompt_message_id"] = msg.message_id
        return WAIT_TITLE


@require_admin
@require_callback_query
async def on_poll_anon_mode(update: Update, context: CallbackContext, query) -> int:
    context.user_data["draft_poll"]["anon_mode"] = query.data.split(":")[-1]

    await query.edit_message_text(
        text="Введите режим ответов:",
        reply_markup=keyboards.poll_answer_mode
    )

    return CHOOSE_ANSWER_MODE


@require_admin
@require_callback_query
async def on_poll_answer_mode(update: Update, context: CallbackContext, query) -> int:
    context.user_data["draft_poll"]["answer_mode"] = query.data.split(":")[-1]

    msg = await query.edit_message_text(
        text="Введите тему опроса:",
        reply_markup=keyboards.poll_message
    )

    context.user_data["prompt_message_id"] = msg.message_id
    return WAIT_TITLE


@require_admin
async def on_poll_title(update: Update, context: CallbackContext) -> int:
    context.user_data["draft_poll"]["title"] = update.message.text

    msg = await update.message.reply_text(
        text="Введите опцию:",
        reply_markup=keyboards.poll_message
    )

    await delete_old_prompt(update=update, context=context)
    context.user_data["prompt_message_id"] = msg.message_id
    return WAIT_OPTIONS


@require_admin
async def on_poll_option(update: Update, context: CallbackContext) -> int:
    options = context.user_data["draft_poll"].get("options", [])
    options.append(update.message.text)
    context.user_data["draft_poll"]["options"] = options

    msg = await update.message.reply_text(
        text="Введите опцию:",
        reply_markup=keyboards.poll_option
    )

    await delete_old_prompt(update=update, context=context)
    context.user_data["prompt_message_id"] = msg.message_id
    return WAIT_OPTIONS


@require_admin
@require_callback_query
async def on_poll_option_finish(update: Update, context: CallbackContext, query) -> int:
    mode = context.user_data["draft_poll"].get("mode")
    options = context.user_data["draft_poll"].get("options", [])

    if mode == "quiz":
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Выберите правильный ответ:",
            reply_markup=keyboards.poll_correct_option_setting(options)
        )

        await delete_old_prompt(update=update, context=context)
        context.user_data["prompt_message_id"] = msg.message_id
        return CHOOSE_CORRECT_OPTION

    return await save_poll(update, context)



@require_admin
@require_callback_query
async def on_poll_correct_option(update: Update, context: CallbackContext, query) -> int:
    option_index = int(query.data.split(":")[-1])
    option_text = context.user_data["draft_poll"]["options"][option_index]
    print(f"CORRECT OPTION INDEX = {option_index}, OPTION TEXT = {option_text}")
    context.user_data["draft_poll"]["correct_option"] = option_text

    await delete_old_prompt(update=update, context=context)
    return await save_poll(update, context)


@require_admin
@require_db_session
async def save_poll(update: Update, context: CallbackContext, session) -> int:
    data = context.user_data.pop("draft_poll")

    is_anon = (data.get("anon_mode") == "anonymous") if data["mode"] == "poll" else False
    is_multi = (data.get("answer_mode") == "multiple") if data["mode"] == "poll" else False
    correct_option = data.get("correct_option")

    await repo.create_poll(
        session=session,
        title=data["title"],
        mode=data["mode"],
        is_anonymous=is_anon,
        allows_multiple_answers=is_multi,
        options=data["options"],
        correct_option=correct_option
    )

    await delete_old_prompt(update=update, context=context)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Опрос успешно создан."
    )
    return ConversationHandler.END


poll_create_conv = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(on_poll_create, pattern="^polls:create$"),
    ],
    states={
        CHOOSE_MODE: [
            CallbackQueryHandler(on_poll_mode, pattern="^polls:mode:(poll|quiz)$")
        ],
        CHOOSE_ANONYMOUS_MODE: [
            CallbackQueryHandler(on_poll_anon_mode, pattern="^polls:anon_mode:(normal|anonymous)$")
        ],
        CHOOSE_ANSWER_MODE: [
            CallbackQueryHandler(on_poll_answer_mode, pattern="^polls:answer_mode:(multiple|single)$")
        ],
        WAIT_TITLE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, on_poll_title)
        ],
        WAIT_OPTIONS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, on_poll_option)
        ],
        CHOOSE_CORRECT_OPTION: [
            CallbackQueryHandler(on_poll_correct_option, pattern="^polls:correct_option:.+$")
        ],
    },
    fallbacks=[
        CallbackQueryHandler(on_poll_option_finish, pattern="^polls:options:finish$"),
        CallbackQueryHandler(on_poll_cancel, pattern="^polls:cancel$")
    ],
)
