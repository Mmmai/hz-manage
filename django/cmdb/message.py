from django.dispatch import Signal

instance_group_relation_updated = Signal()
instance_group_relations_audit = Signal()
instance_bulk_update_audit = Signal()
bulk_creation_audit = Signal()