import os
from dotenv import load_dotenv
from functools import wraps
from typing import Any, Callable, Coroutine
from telegram import Update
from telegram.ext import CallbackContext
from app.core.database import AsyncSessionLocal


load_dotenv()
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID"))
TelegramHandlerFunc = Callable[[Update, CallbackContext], Coroutine[Any, Any, Any]]


def require_db_session(func: Callable[..., Coroutine[Any, Any, Any]]) -> TelegramHandlerFunc:
    @wraps(func)
    async def inner(*args, **kwargs) -> Any:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                kwargs["session"] = session
                return await func(*args, **kwargs)

    return inner


def require_callback_query(func: Callable[..., Coroutine[Any, Any, Any]]) -> TelegramHandlerFunc:
    @wraps(func)
    async def inner(update: Update, context: CallbackContext, *args, **kwargs) -> Any:
        query = update.callback_query
        kwargs["query"] = query
        result = await func(update, context, *args, **kwargs)
        await query.answer()
        return result

    return inner


def require_admin(func: Callable[..., Coroutine[Any, Any, Any]]) -> TelegramHandlerFunc:
    @wraps(func)
    async def inner(update: Update, context: CallbackContext, *args, **kwargs) -> Any:
        if update.effective_user.id != ADMIN_USER_ID:
            return None
        return await func(update, context, *args, **kwargs)

    return inner
