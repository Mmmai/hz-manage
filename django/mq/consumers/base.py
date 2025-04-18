import abc
import logging

logger = logging.getLogger(__name__)


class BaseConsumer(abc.ABC):
    """消费者基类"""

    @abc.abstractmethod
    def process_message(self, message):
        """处理消息的抽象方法"""
        pass

    @abc.abstractmethod
    def start_consuming(self):
        """开始消费的抽象方法"""
        pass

    def handle_error(self, error):
        """错误处理"""
        logger.error(f"消息处理错误: {str(error)}")
