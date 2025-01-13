import shutil
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.plugins.callback import CallbackBase
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible import context
import ansible.constants as C
from ansible.inventory.host import Group, Host
from ansible.executor.playbook_executor import PlaybookExecutor


class ResultCallback(CallbackBase):
    """回调处理类"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}
    
    def v2_runner_on_unreachable(self, result, **kwargs):
        name = result._host.get_name()
        task = result._task.get_name()
        if name in self.host_unreachable:
            self.host_unreachable[name][task] = result._result
        else:
            self.host_unreachable[name] = {task: result._result}
    
    def v2_runner_on_ok(self, result, **kwargs):
        name = result._host.get_name()
        task = result._task.get_name()
        if name in self.host_ok:
            self.host_ok[name][task] = result._result
        else:
            self.host_ok[name] = {task: result._result}
    
    def v2_runner_on_failed(self, result, **kwargs):
        name = result._host.get_name()
        task = result._task.get_name()
        if name in self.host_failed:
            self.host_failed[name][task] = result._result
        else:
            self.host_failed[name] = {task: result._result}


class AnsibleAPI:
    """Ansible API封装类"""
    
    def __init__(self, connection='local', remote_user=None, password=None,
                 inventory=None, sshUser=None, **kwargs):
        # 初始化CLI参数
        context.CLIARGS = ImmutableDict(
            connection=connection,
            remote_user=remote_user,
            inventory=inventory,
            **kwargs
        )
        
        # 初始化基础组件
        self.inventory = inventory
        self.loader = DataLoader()
        self.inv_obj = InventoryManager(loader=self.loader, sources=self.inventory)
        self.passwords = {'conn_pass': password}
        self.results_callback = ResultCallback()
        self.variable_manager = VariableManager(self.loader, self.inv_obj)
    
    def add_host(self, hostip, hostgroup=None, hostport=22, proxy=None):
        self.inv_obj.add_host(host=hostip, group=hostgroup, port=hostport)
        self.variable_manager._extra_vars = {}
        if proxy:
            proxyIp = proxy["proxyIp"]
            self.variable_manager.set_host_variable(
                host=hostip,
                varname='ansible_ssh_common_args',
                value='-o ProxyCommand="ssh -W %h:%p -p 22 -q {user}@{ip}"'.format(user='root', ip=proxyIp)
            )
    
    def run(self, hosts='localhost', gather_facts="no", module='ping', args=''):
        play_source = dict(
            name='Ad-hoc',
            hosts=hosts,
            gather_facts=gather_facts,
            tasks=[{"action": {"module": module, "args": args}}],
        )
        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)
        
        tqm = None
        try:
            tqm = TaskQueueManager(
                inventory=self.inv_obj,
                variable_manager=self.variable_manager,
                loader=self.loader,
                passwords=self.passwords,
                stdout_callback=self.results_callback
            )
            result = tqm.run(play)
        finally:
            if tqm:
                tqm.cleanup()
            shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)
    
    def playbook(self, playbooks, extra_vars={}):
        self.variable_manager._extra_vars = extra_vars
        playbook = PlaybookExecutor(
            playbooks=[playbooks],
            inventory=self.inv_obj,
            variable_manager=self.variable_manager,
            loader=self.loader,
            passwords=self.passwords
        )
        playbook._tqm._stdout_callback = self.results_callback
        result = playbook.run()
        return result
    
    def get_info(self):
        result_raw = {'success': {}, 'failed': {}, 'unreachable': {}}
        for host, result in self.results_callback.host_ok.items():
            for k, v in result.items():
                if host in result_raw['success']:
                    result_raw['success'][host][k] = v
                else:
                    result_raw['success'][host] = {k: v}
        for host, result in self.results_callback.host_failed.items():
            for k, v in result.items():
                if host in result_raw['failed']:
                    result_raw['failed'][host][k] = v
                else:
                    result_raw['failed'][host] = {k: v}
        for host, result in self.results_callback.host_unreachable.items():
            for k, v in result.items():
                if host in result_raw['unreachable']:
                    result_raw['unreachable'][host][k] = v
                else:
                    result_raw['unreachable'][host] = {k: v}
        import json
        print(json.dumps(result_raw, indent=4))
    
    def get_result(self):
        resDict = {}
        for host, result in self.results_callback.host_ok.items():
            if host not in resDict:
                resDict[host] = {}
            changeList = []
            for task, tres in result.items():
                if tres['changed']:
                    changeList.append(tres)
            resDict[host]['success'] = len(result.keys())
            resDict[host]['changed'] = len(changeList)
        
        for host, result in self.results_callback.host_failed.items():
            if host not in resDict:
                resDict[host] = {}
            resDict[host]['failed'] = result
        for host, result in self.results_callback.host_unreachable.items():
            if host not in resDict:
                resDict[host] = {}
            resDict[host]['unreachable'] = result
        return resDict


if __name__ == '__main__':
    ans = AnsibleAPI(password='huizhi123', connection='smart')
    hostip = '180.180.3.21'
    hostip = '12.7.1.231'
    ans.add_host(hostip=hostip, proxy={"proxyIp": '12.7.1.177'})
    ans.run(hosts=hostip, module='ping')
    aaa = ans.get_result()
    print(aaa)
