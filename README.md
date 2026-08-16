# Psychology Telegram Bot

A Telegram bot created for a practicing psychologist to simplify interaction with their clients, 
create interactive experiences, and analyze their preferences.

## Features

- **User interface**
- **Administrator interface (psychologist)**
- **Bot description**
- **Anonymous and non-anonymous feedback** from users to the specialist
- **Creation and completion of quizzes and surveys**
- **Educational materials, announcements, and news**
  - Administrators can upload text, voice messages, videos, video messages, and audio files
  - Users can upload and view content
- **Categorization of educational materials**
- **Bot statistics**

## Commands

- `/start` - start the bot
- `/menu` - open the user menu
- `/admin` - open the admin panel; a personal hidden command available only to the bot administrator (specialist)

## Stack

- Python 3.13
- python-telegram-bot
- AioSqlite

The bot is built using **asynchronous Python**.

## Project Structure

This project completed in **Layered Architecture**

```
app/
    core/
        database.py
    common/
        callbacks.py
        commands.py
        keyboards.py
        messages.py
        texts.py
    utils/
        helpers.py
        wrappers.py
    categories/
        handlers/
            callbacks.py
            convs.py
        keyboards.py
        messages.py
        repo.py
    feedbacks/
    files/
    polls/
    users/
    bot.py
```


## Settings

Create `.env` file

```
BOT_TOKEN=...
ADMIN_USER_ID=...
```

* **BOT_TOKEN** - your bot token obtained from @BotFather.
* **ADMIN_USER_ID** - your Telegram user ID.


## Launch

Locally
```bash
pip install -r requirements.txt
python -m app.bot
```

Docker

```bash
docker compose up --build
```


## Migrations

Automatically during launch
