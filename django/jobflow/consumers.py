from django.http import StreamingHttpResponse
import json,time,os,uuid,shutil
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
from asgiref.sync import sync_to_async
import subprocess
import ansible_runner
import logging
# print(logging.getLogger())
# logger = logging.getLogger('jobflow')
# logger.info("xsdfsafsad")
import logging
logger = logging.getLogger(__name__)
class ws_test(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        logger.info("开始执行命令...")
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
            if error_output:
                await self.send(text_data=json.dumps({
                    'type': 'output',
                    'message': error_output.strip()
                }))
            
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
        logger.info("WebSocket connection accepted for ws_ansible")
        await self.accept()
    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnected with code: {close_code}")
        pass

    async def receive(self, text_data):
        logger.info(f"Received data: {text_data}")
        from node_mg.utils import cmdb_tools
        from node_mg.models import Nodes
        data = json.loads(text_data)
        module = data.get('module')
        module_args = data.get('module_args')
        hosts = data.get('hosts', [])
        
        if not hosts:
            logger.warning("No hosts provided")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': '未提供主机列表'
            }))
            return
        if not module:
            logger.warning("No module provided")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': '未提供Ansible模块'
            }))
            return
        if not module_args and module != 'ping':
            logger.warning("No module arguments provided")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': '未提供Ansible模块参数'
            }))
            return
            
        # 根据hosts获取nodes
        nodes =  Nodes.objects.filter(model_instance_id__in=hosts)
        inventory_data = cmdb_tools.nodes_inventory(nodes)
        logger.info(f"Generated inventory data: {inventory_data}")

        # 创建临时目录
        private_data_dir = "/tmp/ansible_cli/"
        os.makedirs(private_data_dir, exist_ok=True)
        task_dir = os.path.join(private_data_dir, str(uuid.uuid4()))
        os.makedirs(task_dir, exist_ok=True)
        # 发送初始消息
        await self.send(text_data=json.dumps({
            'type': 'output',
            'message': "start run ansible task..."
        }))
        logger.info("Send 'start run ansible task...' message")
        # 记录开始时间
        start_time = time.time()
        try:
            # 异步运行Ansible任务            
            thread, runner = ansible_runner.run_async(
                private_data_dir=task_dir,
                module=module,
                module_args=module_args,
                inventory=inventory_data,
                quiet=True,
                host_pattern="all"
            )
            try:
                for event in runner.events:
                    logger.info(f"Processing event: {event}")
                    if 'stdout' in event and event['stdout']:
                        print(event['stdout'])  
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
            # 等待任务完成
            thread.join()
            # 计算执行时长
            execution_time = time.time() - start_time
            # 发送任务完成消息
            await self.send(text_data=json.dumps({
                'type': 'complete',
                'returncode': runner.rc,
                'execution_time': round(execution_time, 2) 
            }))
            logger.info(f"Task completed with return code: {runner.rc}")

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Exception during ansible execution: {str(e)}", exc_info=True)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'执行出错: {str(e)}',
                'execution_time': round(execution_time, 2)  # 保留两位小数
            }))
        finally:
            # 清理临时目录
            if os.path.exists(task_dir):
                shutil.rmtree(task_dir)