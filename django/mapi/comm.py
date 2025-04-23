from celery.result import AsyncResult
from django.http import StreamingHttpResponse
import time,json
def get_task_status(request, task_id):
    result = AsyncResult(task_id)
    def event_stream():
        # yield "retry: 10000\n\n"
        is_finish = False
        while not is_finish:
            time.sleep(1)
            if result.ready():
                is_finish = True
                yield f"data: {json.dumps({'status':result.state ,'detail': result.result})}\n\n".encode("utf8")
            else:
                # return JsonResponse({'status': 'PENDING'})
                is_finish = False
                res = {"is_finish": False}
                yield f"data: {json.dumps({'status': result.state,'detail':None})}\n\n"
    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream;charset=utf-8")
    response["Cache-Control"] = "no-cache"
    return response