import sqlite3
from datetime import datetime, timedelta


def init_db():
    conn = sqlite3.connect('deadlines.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS deadlines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            task TEXT NOT NULL,
            deadline DATETIME NOT NULL,
            notified_1day BOOLEAN DEFAULT 0,
            notified_2hours BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()


def add_deadline(user_id, subject, task, deadline):
    conn = sqlite3.connect('deadlines.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO deadlines (user_id, subject, task, deadline)
        VALUES (?, ?, ?, ?)
    ''', (user_id, subject, task, deadline))
    conn.commit()
    conn.close()


def get_user_deadlines(user_id):
    conn = sqlite3.connect('deadlines.db')
    c = conn.cursor()
    c.execute('SELECT id, subject, task, deadline FROM deadlines WHERE user_id = ? ORDER BY deadline', (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows


def get_deadlines_for_notification():
    """Получить дедлайны для напоминаний за 1 день и 2 часа"""
    conn = sqlite3.connect('deadlines.db')
    c = conn.cursor()

    now = datetime.now()

    # Дедлайны через 1 день (±30 минут)
    day_target = now + timedelta(days=1)
    day_start = day_target - timedelta(minutes=30)
    day_end = day_target + timedelta(minutes=30)

    # Дедлайны через 2 часа (±15 минут)
    hour_target = now + timedelta(hours=2)
    hour_start = hour_target - timedelta(minutes=15)
    hour_end = hour_target + timedelta(minutes=15)

    c.execute('''
        SELECT id, user_id, subject, task, deadline, notified_1day, notified_2hours 
        FROM deadlines 
        WHERE (deadline BETWEEN ? AND ? AND notified_1day = 0)
           OR (deadline BETWEEN ? AND ? AND notified_2hours = 0)
    ''', (
        day_start.strftime('%Y-%m-%d %H:%M'), day_end.strftime('%Y-%m-%d %H:%M'),
        hour_start.strftime('%Y-%m-%d %H:%M'), hour_end.strftime('%Y-%m-%d %H:%M')
    ))

    rows = c.fetchall()
    conn.close()
    return rows


def mark_notified(deadline_id, notification_type):
    """Пометить дедлайн как уведомленный"""
    conn = sqlite3.connect('deadlines.db')
    c = conn.cursor()

    if notification_type == '1day':
        c.execute('UPDATE deadlines SET notified_1day = 1 WHERE id = ?', (deadline_id,))
    elif notification_type == '2hours':
        c.execute('UPDATE deadlines SET notified_2hours = 1 WHERE id = ?', (deadline_id,))

    conn.commit()
    conn.close()