import pytest
from audit.utils.revert import revert_audit_log
from audit.models import AuditLog

@pytest.mark.django_db
def test_revert_audit_log_create():
    # Create a sample audit log entry
    audit_log = AuditLog.objects.create(
        action='create',
        model_name='TestModel',
        object_id=1,
        changes={'field1': 'old_value', 'field1': 'new_value'},
        user_id=1
    )
    
    # Revert the audit log
    revert_audit_log(audit_log.id)

    # Fetch the reverted object and check its state
    reverted_log = AuditLog.objects.get(id=audit_log.id)
    assert reverted_log.action == 'reverted'
    assert reverted_log.changes == {'field1': 'old_value'}

@pytest.mark.django_db
def test_revert_audit_log_delete():
    # Create a sample audit log entry
    audit_log = AuditLog.objects.create(
        action='delete',
        model_name='TestModel',
        object_id=1,
        changes={'field1': 'old_value'},
        user_id=1
    )
    
    # Revert the audit log
    revert_audit_log(audit_log.id)

    # Check if the object is restored
    assert AuditLog.objects.filter(id=audit_log.object_id).exists() is True

@pytest.mark.django_db
def test_revert_audit_log_invalid_id():
    # Attempt to revert a non-existent audit log
    result = revert_audit_log(9999)  # Assuming 9999 does not exist
    assert result is False  # Expecting the revert function to return False for invalid ID