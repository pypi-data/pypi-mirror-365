import json
import time
import datetime
import six
from six import text_type
from django.http.response import StreamingHttpResponse
#
# if six.PY2:
#     from dwebsocket.decorators import accept_websocket
#     from django.http import HttpResponse
#     from celery.result import AsyncResult
#     import logging
#
#     log = logging.getLogger("django")
#
#
#     @accept_websocket
#     def async_result(request, task_id):
#         def pm(body):
#             try:
#                 if body['status'] in ['FAILURE', 'REVOKED']:
#                     body['result'] = text_type(body['result'])
#                 # print(body)
#                 request.websocket.send(('%s\r' % json.dumps(body)).encode('utf8'))
#             except Exception:
#                 import traceback
#                 log.error("async_result dump json error, body: %s; error: %s", body, traceback.format_exc())
#
#         rs = AsyncResult(task_id)
#         if not request.is_websocket():
#             body = {'status': rs.state, 'result': text_type(rs.result)}
#             return HttpResponse(json.dumps(body))
#
#         else:
#             d = dict(
#                 task_id=rs.task_id,
#                 state=rs.state,
#                 status=rs.status,
#                 result=rs.status == 'FAILURE' and text_type(rs.result) or rs.result,
#                 traceback=rs.traceback
#             )
#             pm(d)
#             try:
#                 r = rs.get(on_message=pm, propagate=False)
#             except Exception as e:
#                 body = {'status': 'FAILURE', 'result': text_type(e)}
#                 request.websocket.send(('%s\r' % json.dumps(body)).encode('utf8'))
# else:
from celery.result import AsyncResult


def generate(task_id):
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
