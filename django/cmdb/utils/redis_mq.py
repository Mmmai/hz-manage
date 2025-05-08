import json
import redis
import logging
from django.conf import settings
from typing import Union, Dict, Any

logger = logging.getLogger(__name__)


class RedisMQ:
    """Redis消息队列工具类"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )

    def publish_message(self, queue_name: str, message: Union[Dict, str]) -> bool:
        """
        发布消息到指定队列
        :param queue_name: 队列名称
        :param message: 消息内容
        :return: 是否发送成功
        """
        try:
            if isinstance(message, dict):
                message = json.dumps(message)
            self.redis_client.lpush(queue_name, message)
            logger.info(f"消息已发送到队列 {queue_name}")
            return True
        except Exception as e:
            logger.error(f"发送消息失败: {str(e)}")
            return False

    def consume_message(self, queue_name: str, timeout: int = 0) -> Union[Dict, str, None]:
        """
        从指定队列消费消息
        :param queue_name: 队列名称
        :param timeout: 等待超时时间(秒)，0表示永久等待
        :return: 消息内容
        """
        try:
            # 使用BRPOP阻塞等待消息
            result = self.redis_client.brpop(queue_name, timeout=timeout)
            if result:
                _, message = result
                try:
                    return json.loads(message)
                except json.JSONDecodeError:
                    return message
            return None
        except Exception as e:
            logger.error(f"消费消息失败: {str(e)}")
            return None
