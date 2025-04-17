from django.http import StreamingHttpResponse
import json,time
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
from asgiref.sync import sync_to_async
import subprocess
class ws_test(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        command = data.get('command')
        
        # 使用subprocess执行Ansible命令
        process = await sync_to_async(subprocess.Popen)(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # 实时读取输出并发送到前端
        while True:
            output = await sync_to_async(process.stdout.readline)()
            if output == '' and process.poll() is not None:
                break
            if output:
                await self.send(text_data=json.dumps({
                    'type': 'output',
                    'message': output.strip()
                }))
        
        # 发送执行完成消息
        await self.send(text_data=json.dumps({
            'type': 'complete',
            'returncode': process.returncode
        }))    


def sse_stream(request):
    a = 10
    def event_stream():
        i = 0
        while True:
            i += 1
            time.sleep(1)  # 模拟实时数据
            yield f"data: {i}\n\n"
            if i > a:
                break
    
    return StreamingHttpResponse(event_stream(), content_type="text/event-stream")

from .tasks import testCelery
from django.http import JsonResponse
from celery.result import AsyncResult

def test_celery(request):
    duration = 60
    task = testCelery.delay(duration=duration)
    return JsonResponse({'task_id': task.id})

def check_task(request, task_id):
    result = AsyncResult(task_id)
    
    if result.ready():
        if result.successful():
            return JsonResponse({'status': 'SUCCESS', 'result': result.result})
        else:
            return JsonResponse({'status': 'FAILURE', 'result': str(result.info)})
    else:
        return JsonResponse({'status': 'PENDING'})