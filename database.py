# database.py
import sqlite3
import json
from datetime import datetime

class Database:
    def __init__(self, db_name='quest_bot.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        # Таблица пользователей
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                language TEXT DEFAULT 'ru',
                stage INTEGER DEFAULT 0,
                paid BOOLEAN DEFAULT 0,
                payment_id TEXT,
                registered_at TIMESTAMP,
                last_activity TIMESTAMP
            )
        ''')
        
        # Таблица для прогресса по этапам
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                user_id INTEGER,
                stage_number INTEGER,
                completed_at TIMESTAMP,
                PRIMARY KEY (user_id, stage_number)
            )
        ''')
        
        # Таблица для статистики
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                date TEXT PRIMARY KEY,
                payments INTEGER DEFAULT 0,
                completions INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()

    def add_user(self, user_id, username, first_name):
        self.cursor.execute('''
            INSERT OR IGNORE INTO users 
            (user_id, username, first_name, registered_at, last_activity)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, datetime.now(), datetime.now()))
        self.conn.commit()

    def set_language(self, user_id, lang):
        self.cursor.execute('UPDATE users SET language = ? WHERE user_id = ?', (lang, user_id))
        self.conn.commit()

    def get_language(self, user_id):
        self.cursor.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 'ru'

    def set_paid(self, user_id, payment_id=None):
        self.cursor.execute('''
            UPDATE users SET paid = 1, payment_id = ? WHERE user_id = ?
        ''', (payment_id, user_id))
        self.conn.commit()
        # Обновляем статистику
        today = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute('''
            INSERT INTO stats (date, payments) VALUES (?, 1)
            ON CONFLICT(date) DO UPDATE SET payments = payments + 1
        ''', (today,))
        self.conn.commit()

    def check_paid(self, user_id):
        self.cursor.execute('SELECT paid FROM users WHERE user_id = ?', (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def get_stage(self, user_id):
        self.cursor.execute('SELECT stage FROM users WHERE user_id = ?', (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def set_stage(self, user_id, stage):
        self.cursor.execute('UPDATE users SET stage = ? WHERE user_id = ?', (stage, user_id))
        self.conn.commit()

    def complete_stage(self, user_id, stage_number):
        self.cursor.execute('''
            INSERT OR IGNORE INTO progress (user_id, stage_number, completed_at)
            VALUES (?, ?, ?)
        ''', (user_id, stage_number, datetime.now()))
        self.conn.commit()
        
        # Если это последний этап (5), обновляем статистику
        if stage_number == 5:
            today = datetime.now().strftime('%Y-%m-%d')
            self.cursor.execute('''
                INSERT INTO stats (date, completions) VALUES (?, 1)
                ON CONFLICT(date) DO UPDATE SET completions = completions + 1
            ''', (today,))
            self.conn.commit()

    def is_stage_completed(self, user_id, stage_number):
        self.cursor.execute('''
            SELECT 1 FROM progress WHERE user_id = ? AND stage_number = ?
        ''', (user_id, stage_number))
        return self.cursor.fetchone() is not None

    def get_stats(self):
        self.cursor.execute('''
            SELECT 
                COUNT(DISTINCT user_id) as total_users,
                SUM(paid) as total_paid,
                COUNT(CASE WHEN stage = 5 THEN 1 END) as completed_quests
            FROM users
        ''')
        result = self.cursor.fetchone()
        return {
            'total_users': result[0] or 0,
            'total_paid': result[1] or 0,
            'completed': result[2] or 0
        }

    def update_activity(self, user_id):
        self.cursor.execute('''
            UPDATE users SET last_activity = ? WHERE user_id = ?
        ''', (datetime.now(), user_id))

        self.conn.commit()
