"""
Django settings for vuedjango project.

Generated by 'django-admin startproject' using Django 3.0.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from pathlib import Path
from celery.schedules import crontab

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# APPEND_SLASH = Fl

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'wt$!m&wf%5yl#ttz!2xxu9&1nrev9xn7dyr0b5g4lj8qzais86'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mlog',
    'mapi',
    'cacheops',
    'cmdb',
    'rest_framework',
    'django_filters',
    'import_export',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'channels',
    'django_celery_beat',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEBUG = True

ROOT_URLCONF = 'vuedjango.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'vuedjango.wsgi.application'
# websocket相关配置
ASGI_APPLICATION = 'vuedjango.asgi.application'
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'manage',
        'USER': 'root',
        'PASSWORD': 'thinker',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },
    'cmdb': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cmdb',
        'USER': 'root',
        'PASSWORD': 'thinker',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },
}
# 多数据库配置
DATABASE_ROUTERS = ['vuedjango.db_router.database_router']
DATABASE_APPS_MAPPING = {
    'mlog': 'default',
    'mapi': 'default',
    'cmdb': 'cmdb',
}

CACHEOPS_REDIS = {
    'host': 'localhost',
    'port': 6379,
    'db': 1,
    'socket_timeout': 3,
    'retry_on_timeout': True,
}

CACHEOPS = {
    'cmdb.modelinstance': {'ops': 'all', 'timeout': 60 * 60},
    'cmdb.modelfields': {'ops': 'all', 'timeout': 60 * 60},
    'cmdb.modelfieldmeta': {'ops': 'all', 'timeout': 60 * 60},
    'cmdb.validationrules': {'ops': 'all', 'timeout': 60 * 60},
}

CACHEOPS_ENABLED = True
CACHEOPS_DEGRADE_ON_FAILURE = True
CACHEOPS_LRU = True
CACHEOPS_DEFAULTS = {
    'timeout': 60 * 60,
    'cache_on_save': True,
    'cache_on_get': True,
    'cache_get_many': True,
    'cache_set_many': True,
    'cache_delete_many': True,
    'local_get': False,
}
# 使用redis作为缓存引擎
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/2',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'timeout': 20,
            },
            'MAX_CONNECTIONS': 1000,
            'PICKLE_VERSION': -1
        },
        'KEY_PREFIX': 'cmdb',
        'TIMEOUT': 3600
    }
}

# Celery配置共享Redis
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/2'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/2'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Shanghai'


SPECTACULAR_SETTINGS = {
    'TITLE': 'CMDB API',
    'DESCRIPTION': 'CMDB系统API文档',
    'VERSION': '1.0.0',
    # UI设置
    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
    'SWAGGER_UI_SETTINGS': {
        # 将所有模型折叠 (不再显示“Schemas”部分)
        'defaultModelsExpandDepth': -1,
        # 折叠具体操作下的请求/响应示例
        'defaultModelExpandDepth': 0,

        'persistAuthorization': True,
    },
    'SERVE_AUTHENTICATION': [],
    # 配置安全认证
    'SECURITY': [
        {
            'ApiKeyAuth': []
        }
    ],

    # 配置认证组件
    'COMPONENT_SPLIT_REQUEST': True,
    'AUTHENTICATION_SCHEMES': {
        'ApiKeyAuth': {
            'type': 'apiKey',
            'in': 'query',
            'name': 'token',
            'description': 'JWT Token 认证（在 URL 参数中携带 token）'
        }
    },

    # 默认所有接口都需要认证
    'DEFAULT_AUTH_REQUIRED': True,

    # 全局分页参数
    'PAGINATION_PARAMETERS': {
        'page': {
            'description': '页码(从1开始)',
            'required': False,
            'default': 1,
        },
        'page_size': {
            'description': '每页数量(默认10,最大100)',
            'required': False,
            'default': 10,
        }
    },
    'TAGS': [
        {
            'name': '通用说明',
            'description': (
                '大部分list接口都支持分页，参数：\n'
                '- page 页码, 默认为1\n'
                '- page_size 每页数量, 默认为10\n\n'
                '部分接口由于响应的结果数量少, 这两个参数将在部分API文档中隐藏'
            )
        },
        {'name': '模型分组管理', 'description': '模型分组相关接口'},
        {'name': '模型管理', 'description': '模型相关接口'},
        {'name': '字段分组管理', 'description': '字段分组相关接口'},
        {'name': '字段校验规则管理', 'description': '字段校验规则相关接口'},
        {'name': '字段管理', 'description': '字段相关接口'},
        {'name': '字段展示管理', 'description': '字段展示设置相关接口'},
        {'name': '字段元数据管理', 'description': '字段元数据相关接口'},
        {'name': '实例唯一性约束管理', 'description': '实例唯一性约束相关接口'},
        {'name': '实例管理', 'description': '实例相关接口'},
        {'name': '模型引用管理', 'description': '模型引用相关接口'},
        {'name': '实例分组管理', 'description': '实例分组相关接口'},
        {'name': '实例分组关联管理', 'description': '实例分组关联相关接口'},
        {'name': '密码及密钥管理', 'description': '密码及密钥相关接口'},
    ],
    # 扩展设置
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/v1',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'PREPROCESSING_HOOKS': [
        'vuedjango.drf_spectacular_hooks.preprocessing_filter_spec',
    ],
    'POSTPROCESSING_HOOKS': [
        'vuedjango.drf_spectacular_hooks.remove_params',
    ],
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
IMPORT_EXPORT_USE_TRANSACTIONS = True
STATIC_URL = '/static/'

# jwt全局认证
REST_FRAMEWORK = {
    # jwt全局认证
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     'rest_framework.permissions.IsAuthenticated',
    # ],
    'DEFAULT_AUTHENTICATION_CLASSES': ['mapi.extensions.jwt_authenticate.JWTQueryParamsAuthentication',],
    # 'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PAGINATION_CLASS': 'mapi.extensions.pagination.StandardResultsSetPagination',

    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

}

LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[{levelname}] {asctime} [{name}] {message}',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'cmdb.log'),
            'formatter': 'standard',
        },
        'celery_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'celery.log'),
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['celery_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
