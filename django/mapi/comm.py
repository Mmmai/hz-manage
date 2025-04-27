from celery.result import AsyncResult
from django.http import StreamingHttpResponse
import time,json,logging
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.core.cache import cache
from cmdb.models import (ZabbixSyncHost)
from rest_framework.response import Response
from rest_framework import status
    
logger = logging.getLogger(__name__)
def get_task_status(request, task_id):
    result = AsyncResult(task_id)
    def event_stream():
        # yield "retry: 10000\n\n"
        is_finish = False
        while not is_finish:
            time.sleep(1)
            if result.ready():
                is_finish = True
                yield f"data: {json.dumps({'status':result.state ,'detail': result.result},ensure_ascii=False)}\n\n".encode("utf8")
            else:
                # return JsonResponse({'status': 'PENDING'})
                is_finish = False
                res = {"is_finish": False}
                yield f"data: {json.dumps({'status': result.state,'detail':None},ensure_ascii=False)}\n\n"
    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream;charset=utf-8")
    response["Cache-Control"] = "no-cache"
    response['X-Accel-Buffering'] = 'no'
    return response

def import_status_sse(request):
    cache_key = request.GET.get('cache_key')
    if not cache_key:
        raise ValidationError({'detail': 'Missing cache key'})
    def event_stream():
        last = None
        for _ in range(600):
            result = cache.get(cache_key)
            if not result:
                yield ValidationError({'detail': 'Cache key not found'})
                break
            current = (result.get('progress'), result.get('status'))
            if current != last:
                last = current
                yield f'data: {result}'
            if result.get('status') in ['completed', 'failed']:
                break
            time.sleep(1)
    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    # response['X-Accel-Buffering'] = 'no'
    return response
def installation_status_sse(request):
    """使用SSE实时获取Zabbix客户端安装状态"""
    try:
        ids = request.GET.get('ids', [])
        all_failed = request.GET.get('all', False)
        if not ids and not all_failed:
            raise ValidationError('缺少sufficient params')
        if all_failed:
            ids = ZabbixSyncHost.objects.filter(agent_installed=False).values_list('id', flat=True)
            ids = [str(id) for id in ids]
        def event_stream():
            last_status = {}
            for _ in range(1200):
                current_status = {}
                hosts = ZabbixSyncHost.objects.filter(id__in=ids).values(
                    'id', 'host_id', 'ip', 'name', 'agent_installed',
                    'interface_available', 'installation_error', 'update_time'
                )
                all_completed = True
                for host in hosts:
                    host_pk = str(host['id'])
                    current_status[host_pk] = host
                    if not host['agent_installed'] and not host['installation_error']:
                        all_completed = False
                if current_status != last_status and current_status:
                    last_status = current_status.copy()
                    data = {
                        'status': 'success',
                        'hosts': list(current_status.values())
                    }
                    yield f"data: {data}\n\n"
                if all_completed:
                    final_data = {
                        'status': 'completed',
                        'hosts': list(current_status.values())
                    }
                    yield f"data: {final_data}\n\n"
                    break
                time.sleep(2)
        response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response
    except Exception as e:
        logger.error(f"Error in get installation status: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'Error in get installation status: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)