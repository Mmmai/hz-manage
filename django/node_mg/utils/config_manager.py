import threading
import logging
import time
import sys
from django.core.cache import cache
from django.apps import apps

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器，用于从数据库读取配置并提供缓存"""

    _instance = None
    _lock = threading.Lock()

    # 配置项名称和默认值
    CONFIG_DEFAULTS = {
        "zabbix_url": "",
        "zabbix_version": "6.0",
        "zabbix_server": "",
        "zabbix_host_template": "",
        "zabbix_ipmi_template": "",
        "zabbix_username": "Admin",
        "zabbix_password": "zabbix",
        "zabbix_interval": "0",
        "zabbix_is_sync": 0,
        "zabbix_network_template": "",
        "asset_auto_update": 1,
    }

    # 缓存超时时间 (秒)
    CACHE_TIMEOUT = 3600

    # 缓存键名
    CACHE_KEY = "config_from_node_mg"

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not getattr(self, '_initialized', False):
            self.config = {}
            self._refresh_timer = None
            self._initialized = True
            self._last_refresh_time = 0

    def load_config(self, force=False):
        current_time = time.time()

        is_migrating = any(arg in ['migrate', 'makemigrations'] for arg in sys.argv)

        # if is_migrating or not force and self.config and (current_time - self._last_refresh_time < 300):
        if is_migrating or not force and self.config:
            return self.config

        cached_config = cache.get(self.CACHE_KEY)
        if cached_config and not force:
            self.config = cached_config
            logger.debug("Loaded Zabbix configuration from cache")
            return self.config

        try:
            from mapi.models import sysConfigParams
            from node_mg.models import ModelConfig
            # 从数据库加载配置
            db_config = {}
            for key, default_value in self.CONFIG_DEFAULTS.items():
                param_name = f"{key}"
                try:
                    param = sysConfigParams.objects.get(param_name=param_name)
                    db_config[key.lower()] = param.param_value
                except sysConfigParams.DoesNotExist:
                    # 如果数据库中不存在，使用默认值
                    db_config[key.lower()] = default_value
                    logger.warning(f"Config {param_name} not found in database, using default: {default_value}")

            if 'interval' in db_config:
                try:
                    db_config['interval'] = int(db_config['interval'])
                except (TypeError, ValueError):
                    db_config['interval'] = 0

            # 添加modelConfig信息到缓存
            for model_config in ModelConfig.objects.filter(is_manage=True):
                db_config[model_config.model.name] = model_config.zabbix_sync_info
            self.config = db_config
            
            cache.set(self.CACHE_KEY, db_config, timeout=self.CACHE_TIMEOUT)

            self._last_refresh_time = current_time

            self._schedule_next_refresh()

            logger.info("Loaded Zabbix configuration from database")
            return self.config

        except Exception as e:
            logger.error(f"Error loading Zabbix configuration from database: {str(e)}")
            if not self.config:
                self.config = {k.lower(): v for k, v in self.CONFIG_DEFAULTS.items()}
            return self.config

    def _schedule_next_refresh(self):
        # 取消现有计时器
        if self._refresh_timer:
            self._refresh_timer.cancel()

        # 设置新计时器 (每小时刷新一次配置)
        self._refresh_timer = threading.Timer(self.CACHE_TIMEOUT, self._safe_refresh_config)
        self._refresh_timer.daemon = True
        self._refresh_timer.start()

    def _safe_refresh_config(self):
        """安全刷新配置，捕获异常防止中断"""
        try:
            self.load_config(force=True)
        except Exception as e:
            logger.error(f"Error refreshing config: {str(e)}")
            # 10分钟后重试
            self._refresh_timer = threading.Timer(600, self._safe_refresh_config)
            self._refresh_timer.daemon = True
            self._refresh_timer.start()

    def get(self, key, default=None):
        """获取配置项值，确保配置已加载"""
        if not self.config:
            self.load_config()
        return self.config.get(key.lower(), default)

    def get_all(self):
        """获取所有配置，确保配置已加载"""
        if not self.config:
            self.load_config()
        return self.config.copy()

    def reload(self):
        """强制重新加载配置"""
        return self.load_config(force=True)

    def is_zabbix_sync_enabled(self):
        """检查 Zabbix 同步是否启用"""
        if not self.config:
            self.load_config()
        is_sync = self.config.get('zabbix_is_sync', 0)
        try:
            return int(is_sync) == 1
        except (ValueError, TypeError):
            return False
    def is_asset_auto_update_enabled(self):
        """检查 Zabbix 同步是否启用"""
        if not self.config:
            self.load_config()
        is_sync = self.config.get('asset_auto_update', 0)
        try:
            return int(is_sync) == 1
        except (ValueError, TypeError):
            return False