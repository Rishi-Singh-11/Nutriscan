"""
database.py — NutriScan Pro's "Accountant"
Handles all SQLite interactions: users, profiles, and meal logs.
"""

import sqlite3
import hashlib
import os
from datetime import date, timedelta
from typing import Optional

DB_PATH = "nutriscan.db"


# ─────────────────────────────────────────────
#  Connection helper
# ─────────────────────────────────────────────

def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row          # Return dict-like rows
    conn.execute("PRAGMA journal_mode=WAL") # Better concurrency
    return conn


# ─────────────────────────────────────────────
#  Schema bootstrap  (called once at startup)
# ─────────────────────────────────────────────

def init_db() -> None:
    with _get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT    NOT NULL UNIQUE,
                password_hash TEXT    NOT NULL,
                created_at    TEXT    DEFAULT (date('now'))
            );

            CREATE TABLE IF NOT EXISTS profiles (
                user_id        INTEGER PRIMARY KEY REFERENCES users(id),
                age            INTEGER,
                weight_kg      REAL,
                height_cm      REAL,
                gender         TEXT,
                activity_level TEXT,
                goal           TEXT,
                daily_cal_goal INTEGER
            );

            CREATE TABLE IF NOT EXISTS meal_logs (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL REFERENCES users(id),
                log_date   TEXT    NOT NULL DEFAULT (date('now')),
                meal_name  TEXT,
                calories   REAL,
                protein_g  REAL,
                carbs_g    REAL,
                fats_g     REAL,
                image_path TEXT
            );
        """)


# ─────────────────────────────────────────────
#  Auth helpers
# ─────────────────────────────────────────────

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(username: str, password: str) -> Optional[int]:
    """INSERT a new user. Returns user_id or None on duplicate."""
    try:
        with _get_conn() as conn:
            cur = conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username.strip().lower(), _hash(password)),
            )
            return cur.lastrowid
    except sqlite3.IntegrityError:
        return None


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """SELECT user row if credentials match, else None."""
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT id, username FROM users WHERE username=? AND password_hash=?",
            (username.strip().lower(), _hash(password)),
        ).fetchone()
    return dict(row) if row else None


# ─────────────────────────────────────────────
#  Profile helpers
# ─────────────────────────────────────────────

def upsert_profile(user_id: int, age: int, weight_kg: float,
                   height_cm: float, gender: str,
                   activity_level: str, goal: str,
                   daily_cal_goal: int) -> None:
    """INSERT or REPLACE a user profile row."""
    with _get_conn() as conn:
        conn.execute("""
            INSERT INTO profiles
                (user_id, age, weight_kg, height_cm, gender,
                 activity_level, goal, daily_cal_goal)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                age=excluded.age, weight_kg=excluded.weight_kg,
                height_cm=excluded.height_cm, gender=excluded.gender,
                activity_level=excluded.activity_level, goal=excluded.goal,
                daily_cal_goal=excluded.daily_cal_goal
        """, (user_id, age, weight_kg, height_cm, gender,
              activity_level, goal, daily_cal_goal))


def get_profile(user_id: int) -> Optional[dict]:
    """SELECT a user's profile. Returns None if not yet created."""
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM profiles WHERE user_id=?", (user_id,)
        ).fetchone()
    return dict(row) if row else None


# ─────────────────────────────────────────────
#  Calorie goal calculator  (Mifflin-St Jeor)
# ─────────────────────────────────────────────

ACTIVITY_MULTIPLIERS = {
    "Sedentary (little/no exercise)":      1.2,
    "Light (1-3 days/week)":               1.375,
    "Moderate (3-5 days/week)":            1.55,
    "Active (6-7 days/week)":              1.725,
    "Very active (hard exercise daily)":   1.9,
}

GOAL_ADJUSTMENTS = {
    "Lose weight":     -500,
    "Maintain weight":    0,
    "Gain muscle":     +300,
}


def calculate_daily_calories(age: int, weight_kg: float, height_cm: float,
                              gender: str, activity_level: str, goal: str) -> int:
    """Mifflin-St Jeor BMR → TDEE → goal-adjusted target."""
    if gender == "Male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    tdee = bmr * ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    goal_adj = GOAL_ADJUSTMENTS.get(goal, 0)
    return max(1200, round(tdee + goal_adj))


# ─────────────────────────────────────────────
#  Meal log helpers
# ─────────────────────────────────────────────

def log_meal(user_id: int, meal_name: str, calories: float,
             protein_g: float, carbs_g: float, fats_g: float,
             image_path: str = "") -> None:
    """INSERT a meal entry for today."""
    with _get_conn() as conn:
        conn.execute("""
            INSERT INTO meal_logs
                (user_id, meal_name, calories, protein_g, carbs_g, fats_g, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, meal_name, calories, protein_g, carbs_g, fats_g, image_path))


def get_today_meals(user_id: int) -> list[dict]:
    """SELECT all meal rows for the current day."""
    with _get_conn() as conn:
        rows = conn.execute("""
            SELECT * FROM meal_logs
            WHERE user_id=? AND log_date=date('now')
            ORDER BY id DESC
        """, (user_id,)).fetchall()
    return [dict(r) for r in rows]


def get_today_totals(user_id: int) -> dict:
    """SELECT summed macros for today."""
    with _get_conn() as conn:
        row = conn.execute("""
            SELECT
                COALESCE(SUM(calories),  0) AS calories,
                COALESCE(SUM(protein_g), 0) AS protein_g,
                COALESCE(SUM(carbs_g),   0) AS carbs_g,
                COALESCE(SUM(fats_g),    0) AS fats_g
            FROM meal_logs
            WHERE user_id=? AND log_date=date('now')
        """, (user_id,)).fetchone()
    return dict(row)


def get_weekly_calories(user_id: int) -> list[dict]:
    """SELECT daily calorie totals for the past 7 days."""
    with _get_conn() as conn:
        rows = conn.execute("""
            SELECT log_date, COALESCE(SUM(calories), 0) AS total_cal
            FROM meal_logs
            WHERE user_id=? AND log_date >= date('now', '-6 days')
            GROUP BY log_date
            ORDER BY log_date ASC
        """, (user_id,)).fetchall()
    # Fill in missing days with 0
    result = {}
    for i in range(6, -1, -1):
        d = (date.today() - timedelta(days=i)).isoformat()
        result[d] = 0
    for row in rows:
        result[row["log_date"]] = row["total_cal"]
    return [{"date": k, "calories": v} for k, v in result.items()]
