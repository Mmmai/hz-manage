import ansible_runner
import logging
import os
from django.conf import settings

logger = logging.getLogger(__name__)


class AnsibleAPI:
    def __init__(self):
        self.private_data_dir = '/tmp/ansible_runner'
        for subdir in ['inventory', 'project', 'artifacts']:
            path = os.path.join(self.private_data_dir, subdir)
            os.makedirs(path, exist_ok=True)
    
    def run_playbook(self, playbook_path, inventory_dict, extra_vars=None):
        """运行playbook并获取结果"""
        try:
            
            result = ansible_runner.run(
                private_data_dir=self.private_data_dir,
                playbook=playbook_path,
                inventory=inventory_dict,
                extravars=extra_vars,
                quiet=True
            )
            # for attrs in dir(result):
            #     print(f'{attrs}: {getattr(result, attrs)}')
            return result
        except Exception as e:
            logger.error(f"Ansible playbook execution failed: {str(e)}")
            return None

    def install_zabbix_agent(self, host_ip, ssh_user='root', ssh_port=22, ssh_pass='thinker'):
        """安装Zabbix客户端"""
        playbook_path = '/opt/zabbix_agent/main.yaml'
        inventory_dict = {
            'zabbix_agent': {
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
                'status': 'success',  # success, failed, unreachable
                'message': '',
                'task_details': []
            }
            for event in result.events:
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
