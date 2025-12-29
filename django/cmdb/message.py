"""
CMDB消息信号模块
定义外部APP需要接收的信号，用于在相关操作发生时触发相应的处理逻辑。
"""

from django.dispatch import Signal

instance_group_relation_updated = Signal()
instance_group_relations_audit = Signal()
instance_bulk_update_audit = Signal()
bulk_creation_audit = Signal()
