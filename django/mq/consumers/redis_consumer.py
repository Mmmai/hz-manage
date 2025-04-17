from .base import BaseConsumer
from django_redis import get_redis_connection
import json
import logging
import time

logger = logging.getLogger(__name__)


class RedisMQConsumer(BaseConsumer):
    """Redis消息队列消费者"""

    def __init__(self, queue_name, conn_name='default'):
        self.queue_name = queue_name
        self.redis_client = get_redis_connection(conn_name)

    def process_message(self, message):
        """
        处理消息的默认实现
        子类应该重写这个方法来实现具体的业务逻辑
        """
        raise NotImplementedError

    def start_consuming(self):
        """开始消费消息"""
        logger.info(f"开始监听队列: {self.queue_name}")
        while True:
            try:
                # 使用BRPOP阻塞等待消息
                result = self.redis_client.brpop(self.queue_name, timeout=1)
                if result:
                    _, message = result
                    try:
                        message_data = json.loads(message)
                        self.process_message(message_data)
                    except json.JSONDecodeError:
                        self.process_message(message)
            except Exception as e:
                self.handle_error(e)
                time.sleep(1)
