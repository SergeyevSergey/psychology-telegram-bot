from uuid import UUID
from telegram import InlineKeyboardMarkup, InlineKeyboardButton


feedback_mode = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("🗣 Обычное сообщение", callback_data="feedbacks:mode:normal")],
        [InlineKeyboardButton("👤 Анонимное сообщение", callback_data="feedbacks:mode:anonymous")],
        [InlineKeyboardButton("❌ Отмена", callback_data="feedbacks:cancel")]
    ]
)


feedback_message = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("❌ Отмена", callback_data="feedbacks:cancel")]
    ]
)


def feedback_paging(offset: int, count: int, feedback_id: UUID) -> InlineKeyboardMarkup:
    prev_offset = (offset - 1) % count
    next_offset = (offset + 1) % count

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("←", callback_data=f"feedbacks:page:{prev_offset}"),
                InlineKeyboardButton(f"{offset + 1}/{count}", callback_data="noop"),
                InlineKeyboardButton("→", callback_data=f"feedbacks:page:{next_offset}"),
            ],
            [
                InlineKeyboardButton("❌ Удалить", callback_data=f"feedbacks:delete:{feedback_id}")
            ],
        ]
    )
