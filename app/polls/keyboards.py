from uuid import UUID
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


poll_admin_menu = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("🔍 Просмотреть опросы", callback_data=f"polls:admin_page:{0}")],
        [InlineKeyboardButton("➕ Добавить опрос", callback_data=f"polls:create")],
    ]
)


poll_mode = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("📋 Опрос", callback_data="polls:mode:poll")],
        [InlineKeyboardButton("🧠 Викторина", callback_data="polls:mode:quiz")],
        [InlineKeyboardButton("❌ Отмена", callback_data="polls:cancel")],
    ]
)


poll_anon_mode = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("🗣 Обычный опрос", callback_data="polls:anon_mode:normal")],
        [InlineKeyboardButton("👤 Анонимный опрос", callback_data="polls:anon_mode:anonymous")],
        [InlineKeyboardButton("❌ Отмена", callback_data="polls:cancel")]
    ]
)


poll_answer_mode = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("🧩 Несколько ответов", callback_data="polls:answer_mode:multiple")],
        [InlineKeyboardButton("🎯 Один ответ", callback_data="polls:answer_mode:single")],
        [InlineKeyboardButton("❌ Отмена", callback_data="polls:cancel")]
    ]
)


poll_message = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("❌ Отмена", callback_data="polls:cancel")]
    ]
)


poll_option = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("🔚 Закончить", callback_data="polls:options:finish")],
        [InlineKeyboardButton("❌ Отмена", callback_data="polls:cancel")]
    ]
)


def poll_correct_option_setting(options: list[str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"{option}", callback_data=f"polls:correct_option:{pos}")]
            for pos, option in enumerate(options)
        ]
    )


def poll_admin_paging(offset: int, count: int, poll_id: UUID) -> InlineKeyboardMarkup:
    prev_offset = (offset - 1) % count
    next_offset = (offset + 1) % count

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("←", callback_data=f"polls:admin_page:{prev_offset}"),
                InlineKeyboardButton(f"{offset + 1}/{count}", callback_data="noop"),
                InlineKeyboardButton("→", callback_data=f"polls:admin_page:{next_offset}"),
            ],
            [
                InlineKeyboardButton("📈 Получить статистику", callback_data=f"polls:stats:{poll_id}")
            ],
            [
                InlineKeyboardButton("❌ Удалить", callback_data=f"polls:delete:{poll_id}")
            ],
        ]
    )


def poll_paging(offset: int, count: int, poll_id: UUID, voted: bool) -> InlineKeyboardMarkup:
    prev_offset = (offset - 1) % count
    next_offset = (offset + 1) % count

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("←", callback_data=f"polls:page:{prev_offset}"),
                InlineKeyboardButton(f"{offset + 1}/{count}", callback_data="noop"),
                InlineKeyboardButton("→", callback_data=f"polls:page:{next_offset}"),
            ],
            [
                InlineKeyboardButton(
                    f"⬇️ {'Показать варианты ответов' if voted else 'Голосовать'}",
                    callback_data=f"polls:options:{poll_id}"
                )
            ],
        ]
    )


def poll_options(option_votes: list, user_votes: set[UUID], total_voters: int, poll) -> InlineKeyboardMarkup:
    keyboard = []
    has_voted = len(user_votes) > 0

    for option, count in option_votes:
        text = option.text

        if poll.mode == "quiz":
            if has_voted:
                if option.id == poll.correct_option_id:
                    text = f"🎯 {option.text}"
                elif option.id in user_votes:
                    text = f"❌ {option.text}"
        else:
            if option.id in user_votes:
                text = f"✅ {option.text}"

        if has_voted:
             text += f" - {(count / total_voters * 100) if total_voters > 0 else 0.0}%"

        keyboard.append([InlineKeyboardButton(text, callback_data=f"polls:vote:{option.id}")])

    if has_voted and poll.mode != "quiz":
        keyboard.append([
            InlineKeyboardButton(
                "🔄 Сбросить выбор" if poll.allows_multiple_answers else "🔄 Отменить голос",
                callback_data=f"polls:retract:{poll.id}"
            )
        ])

    return InlineKeyboardMarkup(keyboard)
