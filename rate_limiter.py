"""
Rate Limiter Module for Legal Research Assistant.
Enforces that only authenticated/identified users can call LLMs,
with a strict quota of 5 requests per day.
"""

import os
import json
from datetime import datetime, date
import threading

project_root = os.path.dirname(os.path.abspath(__file__))
RATE_LIMIT_FILE = os.path.join(project_root, "user_rate_limits.json")
DAILY_LIMIT = 5
CONTACT_EMAIL = "ashishsingh67788@gmail.com"
_rate_limit_lock = threading.Lock()


def _load_rate_limits() -> dict:
    if not os.path.exists(RATE_LIMIT_FILE):
        return {}
    try:
        with open(RATE_LIMIT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_rate_limits(data: dict) -> None:
    try:
        with open(RATE_LIMIT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving rate limits: {e}")


def check_and_increment_rate_limit(user_id: str) -> tuple[bool, int, int]:
    """
    Validates and updates daily usage for a user.
    Returns:
        (is_allowed: bool, remaining_calls: int, daily_limit: int)
    """
    if not user_id or not str(user_id).strip():
        return False, 0, DAILY_LIMIT

    today_str = date.today().isoformat()
    with _rate_limit_lock:
        data = _load_rate_limits()
        user_record = data.get(str(user_id), {})
        last_date = user_record.get("date")
        count = user_record.get("count", 0)

        # Reset count on a new day
        if last_date != today_str:
            count = 0

        # Enforce max 5 queries per day
        if count >= DAILY_LIMIT:
            return False, 0, DAILY_LIMIT

        count += 1
        data[str(user_id)] = {
            "date": today_str,
            "count": count,
            "last_request": datetime.utcnow().isoformat()
        }
        _save_rate_limits(data)
        return True, max(0, DAILY_LIMIT - count), DAILY_LIMIT


def get_user_quota(user_id: str) -> tuple[int, int]:
    """
    Returns current daily quota status without consuming a call.
    Returns:
        (remaining_calls: int, daily_limit: int)
    """
    if not user_id or not str(user_id).strip():
        return 0, DAILY_LIMIT

    today_str = date.today().isoformat()
    with _rate_limit_lock:
        data = _load_rate_limits()
        user_record = data.get(str(user_id), {})
        last_date = user_record.get("date")
        count = user_record.get("count", 0)

        if last_date != today_str:
            return DAILY_LIMIT, DAILY_LIMIT

        remaining = max(0, DAILY_LIMIT - count)
        return remaining, DAILY_LIMIT
