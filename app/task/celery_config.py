from celery.schedules import crontab

CELERY_IMPORTS = "app.worker"
CELERY_TIMEZONE = "UTC"

CELERYBEAT_SCHEDULE = {
    "schedule_crawl_news": {
        "task": "app.worker.crawl_social_scrip",
        "schedule": crontab(minute=0, hour=3),  # Execute daily 3 hour
    }
}
