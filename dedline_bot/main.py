import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from datetime import datetime
from dotenv import load_dotenv
from database import init_db, add_deadline, get_user_deadlines
from notifications import send_notifications

# Загружаем токен из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN") or "7054574702:AAEf5aGu-_3JH9v3SoUHZO6IpP9uk_s9jyA"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🎓 Привет! Я — бот для учёбы.\n\n"
        "Команды:\n"
        "/add — добавить дедлайн\n"
        "/list — посмотреть все дедлайны\n\n"
        "Формат: /add Предмет \"Задание\" ГГГГ-ММ-ДД ЧЧ:ММ\n"
        "Пример: /add Матан \"Лаба 5\" 2025-10-25 23:59"
    )


@dp.message(Command("add"))
async def add_deadline_cmd(message: types.Message):
    try:
        parts = message.text.split(maxsplit=3)
        if len(parts) < 4:
            raise ValueError()
        _, subject, task, datetime_str = parts
        task = task.strip('"')

        # Проверяем формат даты и времени
        deadline_date = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")

        # Проверяем что дедлайн в будущем
        if deadline_date <= datetime.now():
            await message.answer("❌ Дедлайн должен быть в будущем!")
            return

        add_deadline(message.from_user.id, subject, task, datetime_str)
        await message.answer("✅ Дедлайн сохранён!")

    except ValueError:
        await message.answer(
            "❌ Неверный формат.\n"
            "Пример: /add Матан \"Лаба 5\" 2025-10-25 23:59\n"
            "Обязательно указывайте время!",
            parse_mode="Markdown"
        )


@dp.message(Command("list"))
async def list_deadlines(message: types.Message):
    deadlines = get_user_deadlines(message.from_user.id)
    if not deadlines:
        await message.answer("📭 Нет дедлайнов.")
        return
    text = "🗓 Ваши дедлайны:\n\n"
    for d in deadlines:
        deadline_date = datetime.strptime(d[3], "%Y-%m-%d %H:%M")
        days_left = (deadline_date - datetime.now()).days
        text += f"• {d[1]}: *{d[2]}* — {d[3]} (осталось {days_left} дн.)\n"
    await message.answer(text, parse_mode="Markdown")


async def main():
    init_db()
    asyncio.create_task(send_notifications(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())