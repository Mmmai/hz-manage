from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.signals import setup_logging


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vuedjango.settings')

app = Celery('vuedjango')

app.conf.update(
    worker_hijack_root_logger=False,
    worker_log_file='logs/celery.log',
    worker_log_level='INFO',
)

@setup_logging.connect
def config_loggers(*args, **kwargs):
    from logging.config import dictConfig
    from django.conf import settings
    dictConfig(settings.LOGGING)
    
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()