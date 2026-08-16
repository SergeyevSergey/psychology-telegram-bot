from datetime import datetime
from zoneinfo import ZoneInfo


def feedback(username: str | None, text: str, created_at: datetime) -> str:
    return (
        f"Сообщение от {('@'+username) if username else 'Аноним'}:"
        + f"\n\n{text[:4000]}"
        + f"\n\nОтправлено {created_at.astimezone(ZoneInfo('Asia/Tashkent')).strftime('%H:%M %d/%m/%Y')}"
    )
