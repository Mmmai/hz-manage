#!#-*- coding:utf-8 -*-
import ansible_runner

def run_module_async(module, inventory, username, password):
    data_dir = "/tmp/ansible_async"
    inventory_data = {
        "all": {
            "hosts": {
                host: {
                    "ansible_user": username,
                    "ansible_password": password
                } for host in inventory
            }
        }
    }
    
    thread, runner = ansible_runner.run_async(
        private_data_dir=data_dir,
        module=module,
        module_args='hostname',
        inventory=inventory_data,
        quiet=True,
        host_pattern="all"
    )
    
    try:
        for event in runner.events:
            print(event)
            if 'stdout' in event and event['stdout']:
                print(event['stdout'])  
    except Exception as e:
        print(f"Error: {str(e)}")
    
    thread.join()

run_module_async(
    module='shell',
    inventory=['192.168.163.160','192.168.163.161','192.168.163.162','192.168.163.163'],
    username='root',
    password='thinker'
)
