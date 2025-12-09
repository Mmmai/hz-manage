import json
import os
import uuid
import shutil
import ansible_runner
from celery import Celery, current_task, shared_task
import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def run_ansible_task(self, module_args, inventory_data, task_id=None, websocket_group=None):
    """
    运行 Ansible 任务的 Celery 任务函数
    """
    # 创建临时目录
    private_data_dir = "/tmp/ansible_cli/"
    os.makedirs(private_data_dir, exist_ok=True)
    task_dir = os.path.join(private_data_dir, str(uuid.uuid4()) if not task_id else task_id)
    os.makedirs(task_dir, exist_ok=True)
    
    # 获取 channel layer
    channel_layer = get_channel_layer()
    
    try:
        # 定义取消回调函数
        def cancel_callback():
            # 检查任务是否被撤销
            if self.request.called_directly is False:
                try:
                    # 检查任务是否被撤销
                    return self.AsyncResult(self.request.id).state == 'REVOKED'
                except Exception as e:
                    logger.error(f"Error checking task status: {e}")
                    return False
            return False
        
        logger.info(f"Starting Ansible task {self.request.id}")
        
        # 异步运行 Ansible 任务
        thread, runner = ansible_runner.run_async(
            private_data_dir=task_dir,
            module="shell",
            module_args=module_args,
            inventory=inventory_data,
            quiet=False,  # 改为False以确保能捕获到输出
            host_pattern="all",
            cancel_callback=cancel_callback
        )
        
        # 处理事件
        try:
            for event in runner.events:
                # 检查是否被撤销
                if self.request.called_directly is False:
                    if self.AsyncResult(self.request.id).state == 'REVOKED':
                        logger.info("Task has been revoked, stopping execution")
                        runner.canceled = True
                        # 发送任务终止消息
                        if websocket_group and channel_layer:
                            try:
                                async_to_sync(channel_layer.group_send)(
                                    websocket_group,
                                    {
                                        'type': 'ws_ansible.ansible_output',  # 修改类型名称
                                        'message': '任务已被用户终止'
                                    }
                                )
                            except Exception as e:
                                logger.error(f"Error sending termination message: {e}")
                        break
                
                # 处理 stdout 输出
                if 'stdout' in event and event['stdout']:
                    output = event['stdout'].strip()
                    if output:  # 只处理非空输出
                        # 发送输出到 WebSocket 组
                        if websocket_group and channel_layer:
                            try:
                                async_to_sync(channel_layer.group_send)(
                                    websocket_group,
                                    {
                                        'type': 'ws_ansible.ansible_output',  # 修改类型名称
                                        'message': output
                                    }
                                )
                            except Exception as e:
                                logger.error(f"Error sending output message: {e}")
                        
                        # 同时更新任务状态（备选方案）
                        self.update_state(
                            state='PROGRESS',
                            meta={'output': output}
                        )
                
                # 处理 event_data 中的 stdout
                if 'event_data' in event and event['event_data']:
                    event_data = event['event_data']
                    if 'res' in event_data and event_data['res']:
                        res = event_data['res']
                        if 'stdout' in res and res['stdout']:
                            output = res['stdout'].strip()
                            if output:  # 只处理非空输出
                                # 发送输出到 WebSocket 组
                                if websocket_group and channel_layer:
                                    try:
                                        async_to_sync(channel_layer.group_send)(
                                            websocket_group,
                                            {
                                                'type': 'ws_ansible.ansible_output',  # 修改类型名称
                                                'message': output
                                            }
                                        )
                                    except Exception as e:
                                        logger.error(f"Error sending output message: {e}")
                                
                                # 同时更新任务状态（备选方案）
                                self.update_state(
                                    state='PROGRESS',
                                    meta={'output': output}
                                )
        except Exception as e:
            logger.error(f"Error during event processing: {e}")
            # 发送错误消息
            if websocket_group and channel_layer:
                try:
                    async_to_sync(channel_layer.group_send)(
                        websocket_group,
                        {
                            'type': 'ws_ansible.ansible_output',  # 修改类型名称
                            'message': f"事件处理错误: {str(e)}"
                        }
                    )
                except Exception as send_error:
                    logger.error(f"Error sending error message: {send_error}")
            
        # 等待任务完成
        thread.join()
        
        # 检查是否被撤销
        if self.request.called_directly is False:
            if self.AsyncResult(self.request.id).state == 'REVOKED':
                # 发送任务终止消息
                if websocket_group and channel_layer:
                    try:
                        async_to_sync(channel_layer.group_send)(
                            websocket_group,
                            {
                                'type': 'ws_ansible.ansible_complete',  # 修改类型名称
                                'returncode': -1
                            }
                        )
                    except Exception as e:
                        logger.error(f"Error sending completion message: {e}")
                return {'status': 'REVOKED', 'message': 'Task was revoked'}
        
        # 发送任务完成消息
        if websocket_group and channel_layer:
            try:
                async_to_sync(channel_layer.group_send)(
                    websocket_group,
                    {
                        'type': 'ws_ansible.ansible_complete',  # 修改类型名称
                        'returncode': runner.rc
                    }
                )
            except Exception as e:
                logger.error(f"Error sending completion message: {e}")
        
        return {
            'status': 'COMPLETED',
            'returncode': runner.rc,
        }
        
    except Exception as e:
        logger.error(f"Exception during ansible execution: {str(e)}", exc_info=True)
        # 发送错误消息
        if websocket_group and channel_layer:
            try:
                async_to_sync(channel_layer.group_send)(
                    websocket_group,
                    {
                        'type': 'ws_ansible.ansible_output',  # 修改类型名称
                        'message': f"执行错误: {str(e)}"
                    }
                )
            except Exception as send_error:
                logger.error(f"Error sending error message: {send_error}")
        return {'status': 'FAILED', 'error': str(e)}
    finally:
        # 清理临时目录
        if os.path.exists(task_dir):
            try:
                shutil.rmtree(task_dir)
            except:
                pass