from uuid import UUID
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


file_admin_menu = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("🔍 Просмотреть файлы", callback_data=f"files:admin_categories")],
        [InlineKeyboardButton("➕ Добавить файл", callback_data=f"files:create")],
    ]
)


file_message = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("❌ Отмена", callback_data="files:cancel")]
    ]
)


def file_admin_categories(categories) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
    [
        [InlineKeyboardButton(f"{category.name}", callback_data=f"files:admin_page:{0}:{category.id}")]
        for category in categories
    ]
)


def file_categories(categories) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
    [
        [InlineKeyboardButton(f"{category.name}", callback_data=f"files:page:{0}:{category.id}")]
        for category in categories
    ]
)


def file_category(categories) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(f"{category.name}", callback_data=f"files:category:{category.id}")]
        for category in categories
    ]
    keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="files:cancel")])
    return InlineKeyboardMarkup(keyboard)



def files_admin_paging(offset: int, count: int, file_id: UUID, category_id: UUID) -> InlineKeyboardMarkup:
    prev_offset = (offset - 1) % count
    next_offset = (offset + 1) % count

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("←", callback_data=f"files:page:{prev_offset}:{category_id}"),
                InlineKeyboardButton(f"{offset + 1}/{count}", callback_data="noop"),
                InlineKeyboardButton("→", callback_data=f"files:page:{next_offset}:{category_id}"),
            ],
            [InlineKeyboardButton("📥 Скачать", callback_data=f"files:download:{file_id}")],
            [InlineKeyboardButton("❌ Удалить", callback_data=f"files:delete:{file_id}")],
        ]
    )


def files_paging(offset: int, count: int, file_id: UUID, category_id: UUID) -> InlineKeyboardMarkup:
    prev_offset = (offset - 1) % count
    next_offset = (offset + 1) % count

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("←", callback_data=f"files:page:{prev_offset}:{category_id}"),
                InlineKeyboardButton(f"{offset + 1}/{count}", callback_data="noop"),
                InlineKeyboardButton("→", callback_data=f"files:page:{next_offset}:{category_id}"),
            ],
            [InlineKeyboardButton("📥 Скачать", callback_data=f"files:download:{file_id}")],
        ]
    )
