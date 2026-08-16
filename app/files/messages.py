from datetime import datetime
from zoneinfo import ZoneInfo


def file(file_name: str, file_type: str, byte_size: int, created_at: datetime) -> str:
    return (
        f"Название: {file_name}"
        + f"\nТип: {file_type}"
        + f"\nРазмер: {byte_size / 1024 ** 2:.2f} МБ"
        + f"\n\nЗагружено {created_at.astimezone(ZoneInfo('Asia/Tashkent')).strftime('%H:%M %d/%m/%Y')}"
    )
