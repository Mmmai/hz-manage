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
    """使用 SSE 实时获取 Zabbix 安装状态"""
    try:
        cache_key = request.GET.get('cache_key')
        if not cache_key:
            raise ValidationError({'detail': 'Missing cache key'})
        task_info = cache.get(cache_key)
        if not task_info:
            raise ValidationError({'detail': 'Cache key not found'})
        result = {
            'status': 'pending',
            'total': task_info['total'],
            'success': 0,
            'failed': 0,
            'progress': 0
        }
        def event_stream():
            result['status'] = 'processing'
            completed_hosts = set()
            last_progress = 0
            for _ in range(600):
                for zsh_id, task_id in task_info['host_task_map'].items():
                    if zsh_id in completed_hosts:
                        continue
                    check_result = check_chain_task(task_id)
                    if check_result is None:
                        continue
                    elif check_result == 1:
                        result['success'] += 1
                        completed_hosts.add(zsh_id)
                    elif check_result == -1:
                        result['failed'] += 1
                        completed_hosts.add(zsh_id)
                result['progress'] = (result['success'] + result['failed']) // result['total'] * 100
                if result['progress'] == 100:
                    result['status'] = 'completed'
                    yield f"data: {json.dumps(result,ensure_ascii=False)}\n\n"
                    break
                if result['progress'] != last_progress:
                    last_progress = result['progress']
                    yield f"data: {json.dumps(result,ensure_ascii=False)}\n\n"
                # 暂停 2 秒后继续检查
                time.sleep(2)
        # 返回 SSE 响应
        response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response
    except Exception as e:
        logger.error(f"Error in installation status SSE: {str(e)}")
        return Response({
            'error': f'Error in installation status SSE: {str(e)}'
        }, status=500)
    
def check_chain_task(task_id):
    """检查链式任务的状态"""
    task = AsyncResult(task_id)
    if not task.ready():
        return None
    if task.successful():
        if task.result:
            chain_task_id = task.result.get('chain_task_id')
            chain_task = AsyncResult(chain_task_id)
            if not chain_task.ready():
                return None
            if chain_task.successful():
                return 1
            else:
                return -1
        else:
            logger.info(f"Task {task_id} has no result")
            return -1
    else:
        return -1
    # try:
    #     idsStr = request.GET.get('ids', [])
    #     if isinstance(idsStr,str):
    #         ids = json.loads(idsStr)
    #     else:
    #         ids = []
    #     all_failed = request.GET.get('all', False)
    #     if not ids and not all_failed:
    #         raise ValidationError('缺少sufficient params')
    #     if all_failed:
    #         ids = ZabbixSyncHost.objects.filter(agent_installed=False).values_list('id', flat=True)
    #         ids = [str(id) for id in ids]
    #     def event_stream():
    #         last_status = {}
    #         for _ in range(1200):
    #             current_status = {}
    #             hosts = ZabbixSyncHost.objects.filter(id__in=ids).values(
    #                 'id', 'host_id', 'ip', 'name', 'agent_installed',
    #                 'interface_available', 'installation_error'
    #             )
    #             all_completed = True
    #             for host in hosts:
    #                 host_pk = str(host['id'])
    #                 host["id"] = host_pk
    #                 current_status[host_pk] = host
    #                 if not host['agent_installed'] and not host['installation_error']:
    #                     all_completed = False
    #             if current_status != last_status and current_status:
    #                 last_status = current_status.copy()
    #                 data = {
    #                     'status': 'success',
    #                     'hosts': list(current_status.values())
    #                 }
    #                 yield f"data: {json.dumps(data,ensure_ascii=False)}\n\n"
    #             if all_completed:
    #                 final_data = {
    #                     'status': 'completed',
    #                     'hosts': list(current_status.values())
    #                 }
    #                 yield f"data: {json.dumps(final_data,ensure_ascii=False)}\n\n"
    #                 break
    #             time.sleep(2)
    #     response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    #     response['Cache-Control'] = 'no-cache'
    #     response['X-Accel-Buffering'] = 'no'
    #     return response
    # except Exception as e:
    #     logger.error(f"Error in get installation status: {str(e)}")
    #     return Response({
    #         'status': 'error',
    #         'message': f'Error in get installation status: {str(e)}'
    #     }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)