from django.test import TestCase
from audit.models import AuditLog
from django.contrib.auth.models import User

class AuditLogTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.instance_data = {
            'field1': 'value1',
            'field2': 'value2',
        }
        self.audit_log = AuditLog.objects.create(
            user=self.user,
            action='create',
            instance_data=self.instance_data,
            model_name='TestModel'
        )

    def test_audit_log_creation(self):
        self.assertEqual(AuditLog.objects.count(), 1)
        self.assertEqual(self.audit_log.action, 'create')
        self.assertEqual(self.audit_log.user.username, 'testuser')
        self.assertEqual(self.audit_log.instance_data, self.instance_data)

    def test_audit_log_retrieval(self):
        logs = AuditLog.objects.all()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].instance_data, self.instance_data)

    def test_audit_log_update(self):
        self.audit_log.action = 'update'
        self.audit_log.save()
        updated_log = AuditLog.objects.get(id=self.audit_log.id)
        self.assertEqual(updated_log.action, 'update')

    def test_audit_log_deletion(self):
        self.audit_log.delete()
        self.assertEqual(AuditLog.objects.count(), 0)