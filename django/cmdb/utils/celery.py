import logging
from celery.app import default_app

logger = logging.getLogger(__name__)


class CeleryManager:

    @staticmethod
    def check_heartbeat():
        """检查Celery心跳"""
        try:
            inspector = default_app.control.inspect()

            # 获取worker心跳
            ping = inspector.ping()
            if not ping:
                logger.error("No workers responded to ping")
                return False

            return True

        except Exception as e:
            logger.error(f"Heartbeat check failed: {str(e)}", exc_info=True)
            return False
