from celery import Celery

from app.core.config import settings
from app.task import celery_config


def make_celery():
    celery = Celery(
        "worker", backend=settings.CELERY_RESULT_BACKEND, broker=settings.CELERY_BROKER
    )
    celery.conf.update(settings)
    celery.config_from_object(celery_config)

    return celery


celery_app = make_celery()
