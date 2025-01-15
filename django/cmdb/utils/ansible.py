import shutil
import uuid
import ansible_runner
import logging
import os
from django.conf import settings

logger = logging.getLogger(__name__)


class AnsibleAPI:
    def __init__(self):
        self.private_data_dir = '/tmp/ansible_runner'
        os.makedirs(self.private_data_dir, exist_ok=True)

    def run_playbook(self, playbook_path, inventory_dict, extra_vars=None):
        """运行playbook并获取结果"""
        try:
            # 为每个任务创建唯一的临时目录，避免多个任务创建时inventory被覆盖导致无法匹配IP
            task_dir = os.path.join(self.private_data_dir, str(uuid.uuid4()))
            os.makedirs(task_dir, exist_ok=True)
            for subdir in ['env', 'inventory', 'project', 'artifacts']:
                path = os.path.join(task_dir, subdir)
                os.makedirs(path, exist_ok=True)

            result = ansible_runner.run(
                private_data_dir=task_dir,
                playbook=playbook_path,
                inventory=inventory_dict,
                extravars=extra_vars,
                quiet=False
            )
            # 立刻解析结果，避免在调用方等待时临时目录被清理
            events = list(result.events)
            status = {
                'rc': result.rc,
                'status': result.status,
                'events': events
            }
            return status

        except Exception as e:
            logger.error(f"Ansible playbook execution failed: {str(e)}")
            return None
        finally:
            # 清理临时目录
            if os.path.exists(task_dir):
                shutil.rmtree(task_dir)

    def install_zabbix_agent(self, host_ip, ssh_user, ssh_port, ssh_pass):
        """安装Zabbix客户端"""
        playbook_path = '/opt/zabbix_agent/main.yaml'
        inventory_dict = {
            'all': {
                'hosts': {
                    host_ip: {
                        'ansible_ssh_user': ssh_user,
                        'ansible_ssh_pass': ssh_pass,
                        'ansible_ssh_port': ssh_port,
                        'ansible_ssh_common_args': '-o StrictHostKeyChecking=no'
                    }
                }
            }
        }
        server = getattr(settings, 'ZABBIX_SERVER', {}).get('server')
        extra_vars = {
            'hostIp': host_ip,
            'serverIp': server,
            'serverActiveIp': server,
            'inventory_hostname': host_ip
        }
        result = self.run_playbook(playbook_path, inventory_dict, extra_vars)
        if result:
            installation_status = {
                'status': 'success',
                'message': '',
                'task_details': []
            }
            for event in result.get('events'):
                if event.get('event') in ['runner_on_failed', 'runner_on_unreachable']:
                    event_data = event.get('event_data', {})
                    task_name = event_data.get('task', 'unknown')
                    error_msg = event_data.get('res', {}).get('msg', 'No error message')
                    ignore_errors = event_data.get('ignore_errors', False)

                    if not ignore_errors:
                        if event.get('event') == 'runner_on_failed':
                            installation_status['status'] = 'failed'
                            installation_status['message'] = f"Task '{task_name}' failed: {error_msg}"
                        else:
                            installation_status['status'] = 'unreachable'
                            installation_status['message'] = f"Host unreachable: {error_msg}"

                    installation_status['task_details'].append({
                        'task': task_name,
                        'status': 'ignored' if ignore_errors else installation_status['status'],
                        'message': error_msg
                    })
                    break
            if installation_status['status'] == 'success':
                logger.info(f'Installation for {host_ip} completed with status: {installation_status["status"]}')
            else:
                logger.error(f'Installation for {host_ip} failed with status: {installation_status["status"]}'
                             f' and message: {installation_status["message"]}'
                             f' and task details: {installation_status["task_details"]}')
            logger.info(f'Parsed installation result for {host_ip}: {installation_status}')
            return installation_status
        logger.error(f'Installation for {host_ip} failed, no result found')
        return {
            'status': 'unknown'
        }


def main():

    host_ip = '192.168.137.2'
    ansible_api = AnsibleAPI()
    result = ansible_api.install_zabbix_agent(host_ip)

    if result:
        print(f"\nZabbix agent installation result for {host_ip}:")
        print(f"Status: {result['status']}")
        if result['status'] != 'success':
            print(f"Error: {result['message']}")
            print("\nTask Details:")
            for task in result['task_details']:
                print(f"- Task: {task['task']}")
                print(f"  Status: {task['status']}")
                print(f"  Message: {task['message']}")
    else:
        print(f"Failed to execute playbook for {host_ip}")


if __name__ == "__main__":
    main()
