from django.contrib import admin
from .models import AuditLog

class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'action', 'instance_id', 'timestamp', 'user')
    search_fields = ('instance_id', 'action', 'user__username')
    list_filter = ('action', 'timestamp')

admin.site.register(AuditLog, AuditLogAdmin)