from django.http import StreamingHttpResponse
import json,time,os,uuid,shutil
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
from asgiref.sync import sync_to_async
import subprocess
import ansible_runner
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


class ws_ansible(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        module_args = data.get('module_args')
        module_name = data.get('module')
        username = data.get('username')
        password = data.get('password')
        inventory = data.get('inventory')
        await self.send(text_data=json.dumps({
                        'type': 'output',
                        'message': inventory
                        }))
        private_data_dir = "/tmp/ansible_async/"
        inventory = ["192.168.163.160","192.168.163.161","192.168.163.11","192.168.163.12"]
        inventory_data = {
            "all": {
                "hosts": {
                    host: {
                        "ansible_user": "root",
                        "ansible_password": "thinker"
                    } for host in inventory
                }
            }
        }
        os.makedirs(private_data_dir, exist_ok=True)
        # 创建临时目录
        task_dir = os.path.join(private_data_dir, str(uuid.uuid4()))
        os.makedirs(task_dir, exist_ok=True)

        thread, runner = ansible_runner.run_async(
            private_data_dir=task_dir,
            module="shell",
            module_args=module_args,
            inventory=inventory_data,
            quiet=True,
            host_pattern="all"
        )

        try:
            for event in runner.events:
                # print(event)

                if 'stdout' in event and event['stdout']:
                    # print(event['stdout'])  
                    await self.send(text_data=json.dumps({
                        'type': 'output',
                        'message': event['stdout'].strip()
                        }))
        except Exception as e:
            print(f"Error: {str(e)}")
            await self.send(text_data=json.dumps({
                        'type': 'output',
                        'message': event['stdout'].strip()
                        }))
        finally:
            # 清理临时目录
            if os.path.exists(task_dir):
                shutil.rmtree(task_dir)
            thread.join()

        # 发送执行完成消息
        await self.send(text_data=json.dumps({
            'type': 'complete',
            # 'returncode': thread.returncode
        }))    


