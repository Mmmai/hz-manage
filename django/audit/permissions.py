from django.contrib.auth.models import User, Permission
from rest_framework import permissions

class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit audit logs.
    """

    def has_permission(self, request, view):
        # Allow read-only access to any user
        if request.method in permissions.SAFE_METHODS:
            return True
        # Allow write access only to admin users
        return request.user and request.user.is_staff

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an audit log to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Allow read-only access to any user
        if request.method in permissions.SAFE_METHODS:
            return True
        # Allow write access only to the owner of the audit log
        return obj.user == request.user

class CanRevertAuditLog(permissions.BasePermission):
    """
    Custom permission to allow users to revert audit logs.
    """

    def has_permission(self, request, view):
        # Allow access only to users with the 'can_revert_audit_log' permission
        return request.user.has_perm('audit.can_revert_audit_log')