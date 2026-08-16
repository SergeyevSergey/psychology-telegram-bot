from uuid import UUID
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


category_admin_menu = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("🔍 Просмотреть категории", callback_data=f"categories:page:{0}")],
        [InlineKeyboardButton("➕ Добавить категорию", callback_data=f"categories:create")],
    ]
)


category_name = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("❌ Отменить", callback_data=f"categories:cancel")]
    ]
)


def categories_paging(offset: int, count: int, category_id: UUID) -> InlineKeyboardMarkup:
    prev_offset = (offset - 1) % count
    next_offset = (offset + 1) % count

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("←", callback_data=f"categories:page:{prev_offset}"),
                InlineKeyboardButton(f"{offset + 1}/{count}", callback_data="noop"),
                InlineKeyboardButton("→", callback_data=f"categories:page:{next_offset}"),
            ],
            [InlineKeyboardButton("✍️ Переименовать", callback_data=f"categories:update:{category_id}")],
            [InlineKeyboardButton("❌ Удалить", callback_data=f"categories:delete:{category_id}")],
        ]
    )
