import logging

from .celery_app import celery

logger = logging.getLogger(__name__)


@celery.task(name="gearpulse.notify_subscription", autoretry_for=(RuntimeError,), retry_backoff=True, max_retries=3)
def notify_subscription(payload: dict) -> dict:
    """Background notification boundary; replace log delivery with SES when credentials exist."""
    logger.info(
        "subscription_activated user_id=%s plan=%s",
        payload.get("user_id"),
        payload.get("plan"),
    )
    return {"delivered": True, "channel": "audit-log", "user_id": payload.get("user_id")}


@celery.task(name="gearpulse.generate_workout_report", autoretry_for=(RuntimeError,), retry_backoff=True, max_retries=3)
def generate_workout_report(payload: dict) -> dict:
    duration = float(payload.get("duration_minutes", 0))
    calories = int(payload.get("calories", 0))
    report = {
        "workout_id": payload.get("id"),
        "duration_minutes": duration,
        "calories": calories,
        "calories_per_minute": round(calories / duration, 2) if duration > 0 else 0,
    }
    logger.info("workout_report generated=%s", report)
    return report
