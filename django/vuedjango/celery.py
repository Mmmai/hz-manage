from __future__ import absolute_import, unicode_literals
from math import log
import os
import sys
import time
import logging
from celery import Celery
from celery.signals import setup_logging
from datetime import timedelta
from cmdb.utils import zabbix_config

logger = logging.getLogger(__name__)

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

is_migrating = any(arg in ['migrate', 'makemigrations'] for arg in sys.argv)

if not is_migrating:

    beat_schedule = {}
    if zabbix_config.is_zabbix_sync_enabled():
        # 只在启用同步时添加 Zabbix 相关任务
        beat_schedule.update({
            'update-zabbix-interface-every-5-minutes': {
                'task': 'cmdb.tasks.update_zabbix_interface_availability',
                'schedule': timedelta(minutes=1),
            }
        })
        logger.info("Zabbix sync is enabled, added Zabbix related tasks to beat schedule")
    else:
        logger.warning("Zabbix sync is disabled, skipping Zabbix related tasks in beat schedule")

    app.conf.beat_schedule = beat_schedule
