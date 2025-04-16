from celery import chain, shared_task
import time
@shared_task
def testCelery(duration):
    time.sleep(duration)  # 模拟耗时操作
    return f"任务完成，等待了 {duration} 秒。"