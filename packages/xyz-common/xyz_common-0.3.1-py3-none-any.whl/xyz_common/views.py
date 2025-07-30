import json
import time
import datetime
import six
from six import text_type
from django.http.response import StreamingHttpResponse

def generate(task_id):
    from celery.result import AsyncResult
    t = AsyncResult(task_id)
    c = t.backend.result_consumer
    c.start(t.id)
    p = c._pubsub
    if not p.subscribed:
        p.subscribe(c.subscribed_to)
    while True:
        t.backend.result_consumer.drain_events()
        rd = {"task_id": t.id, "status": t.status}
        if t.status == "FAILURE":
            rd["error"] = t.result
        else:
            rd["result"] = t.result
        yield "data: %s\n\n" % json.dumps(rd)
        if t.status in ['FAILURE', 'REVOKED', 'SUCCESS']:
            return


def async_result(request, task_id):
    return StreamingHttpResponse(generate(task_id), content_type='text/event-stream')
