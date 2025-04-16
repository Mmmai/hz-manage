from django.http import StreamingHttpResponse
import time

def sse_stream(request):
    a = 10
    def event_stream():
        i = 0
        while True:
            i += 1
            time.sleep(1)  # 模拟实时数据
            yield f"data: {i}\n\n"
            if i > a:
                break
    
    return StreamingHttpResponse(event_stream(), content_type="text/event-stream")

from .tasks import testCelery
from django.http import JsonResponse
from celery.result import AsyncResult

def test_celery(request):
    duration = 60
    task = testCelery.delay(duration=duration)
    return JsonResponse({'task_id': task.id})

def check_task(request, task_id):
    result = AsyncResult(task_id)
    
    if result.ready():
        if result.successful():
            return JsonResponse({'status': 'SUCCESS', 'result': result.result})
        else:
            return JsonResponse({'status': 'FAILURE', 'result': str(result.info)})
    else:
        return JsonResponse({'status': 'PENDING'})