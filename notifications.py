import asyncio
from datetime import datetime, timedelta
from database import get_deadlines_for_notification

async def send_notifications(bot):
    while True:
        now = datetime.now()
        next_run = now.replace(hour=8, minute=0, second=0, microsecond=0)
        if now >= next_run:
            next_run += timedelta(days=1)
        sleep_seconds = (next_run - now).total_seconds()
        await asyncio.sleep(sleep_seconds)

        today = datetime.now().date().isoformat()
        tomorrow = (datetime.now().date() + timedelta(days=1)).isoformat()

        for label, date_str in [("СЕГОДНЯ", today), ("ЗАВТРА", tomorrow)]:
            deadlines = get_deadlines_for_notification(date_str)
            for user_id, subject, task, _ in deadlines:
                try:
                    await bot.send_message(
                        user_id,
                        f"⏰ *Напоминание!*\n"
                        f"Дедлайн по предмету *{subject}* — {label}!\n"
                        f"Задание: {task}",
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    print(f"Ошибка отправки {user_id}: {e}")