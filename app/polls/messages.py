from app.core.database import PollOption, Poll


def poll_admin(poll: Poll, options: list[PollOption]) -> str:
    return (
        f"Тема опроса: {poll.title}"
        + f"\nТип опроса: {'викторина' if poll.mode == 'quiz' else 'простой опрос'}"
        + f"\nМножественные ответы: {'разрешены' if poll.allows_multiple_answers else 'запрещены'}"
        + f"\nАнонимный: {'да' if poll.is_anonymous else 'нет'}"
        + "\n\nВарианты ответов:\n"
        + "\n".join(
            f"{option.position} - {'🎯' if option.id == poll.correct_option_id else ''} {option.text}"
            for option in options
        )
    )


def poll(poll: Poll) -> str:
    return (
        f"Тема опроса: {poll.title}"
        + f"\nТип опроса: {'викторина' if poll.mode == 'quiz' else 'простой опрос'}"
        + f"\nМножественные ответы: {'разрешены' if poll.allows_multiple_answers else 'запрещены'}"
        + f"\nАнонимный: {'да' if poll.is_anonymous else 'нет'}"
    )


def poll_stats(options_votes: list[tuple[PollOption, int]], total_voters: int,) -> str:
    return (
        f"Статистика по опросу:\n"
        +"\n\n".join(
            f"{option.position} - {option.text}\n процент голосовавших: {(count / total_voters * 100) if total_voters > 0 else 0.0}%"
            for option, count in options_votes
        )
    )

