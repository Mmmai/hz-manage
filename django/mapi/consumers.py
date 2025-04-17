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
            error_output = await sync_to_async(process.stderr.readline)()
            await self.send(text_data=json.dumps({
                        'type': 'output',
                        'message': error_output.strip()
                    }))
            # print(123)
            # print(error_output)
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


