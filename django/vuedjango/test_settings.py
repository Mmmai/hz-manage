"""
测试环境专用配置
使用方式: python manage.py test --settings=vuedjango.test_settings
"""
from vuedjango.settings import *  # noqa: F401, F403

# 覆盖数据库为 SQLite 内存数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# 禁用 cacheops
CACHEOPS_ENABLED = False
CACHEOPS = {}
CACHEOPS_REDIS = None

# 使用本地内存缓存替代 Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'KEY_PREFIX': 'test_cmdb',
    }
}

# 从 INSTALLED_APPS 中移除 cacheops
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'cacheops']  # noqa: F405

# 从 MIDDLEWARE 中移除 cacheops 相关中间件
MIDDLEWARE = [  # noqa: F405
    m for m in MIDDLEWARE  # noqa: F405
    if 'cacheops' not in m.lower()
]

# Celery 同步执行
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# 禁用 CMDB 初始化信号（避免创建内置数据与测试数据冲突）
SILENCED_SYSTEM_CHECKS = ['*']

# 禁用日志文件输出（测试时不需要）
LOGGING['handlers'] = {  # noqa: F405
    'console': {
        'level': 'WARNING',
        'class': 'logging.StreamHandler',
        'formatter': 'standard',
    }
}
LOGGING['loggers'] = {  # noqa: F405
    'django': {
        'handlers': ['console'],
        'level': 'WARNING',
        'propagate': False,
    },
    'cmdb': {
        'handlers': ['console'],
        'level': 'WARNING',
        'propagate': False,
    },
}
