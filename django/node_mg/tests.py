# from django.test import TestCase

# # Create your tests here.
# from .utils.cmdb_tools import get_instance_field_value,get_instance_field_value_info
# from cmdb.models import ModelInstance

# obj = ModelInstance.objects.get(id="6e4ec8067a8a40308078769a9bf034a8")
# print(get_instance_field_value(obj, 'device_status'))
# print(get_instance_field_value_info(obj, ['mgmt_user','mgmt_password','mgmt_ip','device_status']))



# def compare_interfaces1(old, new):
#     def to_hashable(d):
#         return d['type']  # 仅以 'type' 作为唯一标识

#     # 按 'type' 分组，快速定位新增/删除
#     old_dict = {to_hashable(d): d for d in old}
#     new_dict = {to_hashable(d): d for d in new}

#     # 新增和删除的接口
#     added = [d for t, d in new_dict.items() if t not in old_dict]
#     removed = [d for t, d in old_dict.items() if t not in new_dict]

#     # 修改的接口（仅比较 'type' 相同的项）
#     modified = []
#     common_types = set(old_dict.keys()) & set(new_dict.keys())
#     for t in common_types:
#         old_d = old_dict[t]
#         new_d = new_dict[t]
#         # 排除 'type' 自身，比较其他字段
#         diff = {k: (old_d[k], new_d[k]) for k in old_d if k != 'type' and old_d[k] != new_d[k]}
#         if diff:  # 仅在存在差异时记录
#             modified.append(diff)

#     return added, removed, modified
# def compare_interfaces(old, new):
#     def to_hashable(d):
#         return d['type']  # 仅以 'type' 作为唯一标识

#     # 按 'type' 分组，快速定位新增/删除
#     old_dict = {to_hashable(d): d for d in old}
#     new_dict = {to_hashable(d): d for d in new}

#     # 新增和删除的接口
#     added = [d for t, d in new_dict.items() if t not in old_dict]
#     removed = [d for t, d in old_dict.items() if t not in new_dict]

#     # 修改的接口（仅比较 'type' 相同的项）
#     modified = []
#     common_types = set(old_dict.keys()) & set(new_dict.keys())
#     for t in common_types:
#         old_d = old_dict[t]
#         new_d = new_dict[t]
#         # 排除 'type' 自身，比较其他字段是否有差异
#         if old_d != new_d:
#             modified.append(new_d)  # 返回完整的 new_dict

#     return added, removed, modified
# # 调用函数
# old_interfaces = [{'type': 1, 'main': 1, 'useip': 1, 'ip': '192.168.163.123', 'port': '10050', 'dns': ''}, {'type': 3, 'main': 1, 'useip': 1, 'ip': '10.10.10.11', 'port': '623', 'dns': ''}]
# new_interfaces = [{'type': 1, 'main': 1, 'useip': 1, 'ip': '192.168.163.123', 'port': '10050', 'dns': ''},{'type': 3, 'main': 1, 'useip': 1, 'ip': '10.10.10.12', 'port': '623', 'dns': ''}]

# added, removed, modified = compare_interfaces(old_interfaces, new_interfaces)

# print("新增接口:", added)
# print("删除接口:", removed)
# print("修改接口:", modified)
from cmdb.models import ModelInstance
from .utils.cmdb_tools import get_instance_field_value,get_instance_field_value_info,update_asset_info
# print(123)
info = {'os_name': 'RedHat 7.4', 'serial_number': 'VMware-56 4d 4c 32 e1 91 70 bb-b5 68 c2 d9 aa 2a 8d 91', 'hardware_info': "{'name': 'VMware Virtual Platform', 'vendor': 'VMware, Inc.', 'serial_number': 'VMware-56 4d 4c 32 e1 91 70 bb-b5 68 c2 d9 aa 2a 8d 91'}", 'hostname': 'localhost', 'disk_size': '40.0', 'cpu_info': "{'model': 'AMD Ryzen 7 8845HS w/ Radeon 780M Graphics', 'cores': 8}", 'os_arch': 'x86_64', 'memory_info': "{'total_gb': '3.69'}", 'os_type': 'linux', 'os_version': '7.4'}
obj = ModelInstance.objects.get(id="f59bef929aa24dd89d09c54ea3928735")
# print(obj)
# print(get_instance_field_value(obj, 'ip'))
print(get_instance_field_value_info(obj, info.keys()))
update_asset_info(obj,info)