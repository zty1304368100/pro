import json
import time
from users.models import UserProfile
from django.test import TestCase

# Create your tests here.

from django.http import StreamingHttpResponse
from django.utils.timezone import now
from django.views import View
from rest_framework.views import APIView

from eslcampus.settings import REDIS_CONN


class EventSource(APIView):
    # class EventSource(View):
    #     authentication_classes = []
    def get(self, request):
        # print(request.user)
        print(request)
        response = StreamingHttpResponse(stream_generator(request.user.username), content_type="text/event-stream")
        response['Cache-Control'] = 'no-cache'
        return response


def stream_generator(username):
    num = 0
    while True:
        # 发送事件数据
        if REDIS_CONN.llen(username) != 0:
            #clear list
            REDIS_CONN.ltrim(username, 1, 0)

            # send 1 to frontend
            msg = u"1"
            yield msg

            time.sleep(1)

            # send 0 to frontend
            msg = u"0"
            yield msg
        else:
            time.sleep(3)
            continue


class MessageInfo(View):

    #     authentication_classes = []

    def msg_stream_generator(self, username):
        while True:
            # 发送事件数据
            # yield 'event: date\ndata: %s\n\n' % str(now())
            if REDIS_CONN.exists(username):
                if REDIS_CONN.llen(username) > 0:
                    yield '{"error_code":0,"detail":"ok"}'
                    REDIS_CONN.delete(username)

                msg = REDIS_CONN.get(username).decode('utf8')
                # print(msg)
                msg1 = json.loads(msg)
                if msg1.get('error_code') == 1:
                    yield u'data: %s\n\n' % msg
                    REDIS_CONN.set(username, '{"error_code":0,"detail":"ok"}')
                # yield '%s\n\n' % msg

            else:
                yield u'data: %s\n\n' % '{"error_code":0,"detail":"ok"}'
                REDIS_CONN.set(username, '{"error_code":0,"detail":"ok"}')

                continue

    def get(self, request):
        token = request.GET.get('token')
        user_obj = UserProfile.objects.filter(token=token).first()
        REDIS_CONN.set(user_obj.username, '{"error_code":1,"detail":"ok"}')
        response = StreamingHttpResponse(self.msg_stream_generator(user_obj.username),
                                         content_type="text/event-stream")
        response['Cache-Control'] = 'no-cache'
        return response
# =======
#             #TODO:nothing
#             time.sleep(3)
#             continue
#
#
# >>>>>>> Stashed changes
