import time
import json
import logging

from celery.result import AsyncResult
from django.http import StreamingHttpResponse
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, PermissionDenied

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
        print(cache_key)
        if not cache_key:
            raise ValidationError({'detail': 'Missing cache key'})
        task_info = cache.get(cache_key)
        print(task_info)
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
                    print(task_id)
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
            print(task.result)
            chain_task_id = task.result.get('chain_task_id')
            print(chain_task_id)
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
