def stats(
        user_count: int,
        feedback_count: int,
        category_count: int,
        file_count: int,
        poll_count: int
) -> str:
    return (
        f"Суммарная статистика по боту:"
        + f"\n👥 Пользователи: {user_count}"
        + f"\n💬 Отзывы: {feedback_count}"
        + f"\n🗂️ Категории: {category_count}"
        + f"\n📁 Файлы: {file_count}"
        + f"\n📊 Опросы: {poll_count}"
    )

