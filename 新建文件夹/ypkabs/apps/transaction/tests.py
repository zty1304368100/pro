import json
import socket
import time

# from django.test import TestCase
#
# # Create your tests here.
#
# from django.http import StreamingHttpResponse
# from django.utils.timezone import now
# from eslcampus.settings import REDIS_CONN
#
# def eventsource(request):
#     response = StreamingHttpResponse(stream_generator('156'), content_type="text/event-stream")
#     response['Cache-Control'] = 'no-cache'
#     return response
#
#
# def stream_generator(username):
#     while True:
#         # 发送事件数据
#         # yield 'event: date\ndata: %s\n\n' % str(now())
#         if REDIS_CONN.exists(username):
#             msg = REDIS_CONN.get(username).decode('utf8')
#             print(msg)
#             yield u'data: %s\n\n' % msg
#             time.sleep(10)
#         else:
#             time.sleep(2)
#             continue
#         # 发送数据
#         # yield u'data: %s\n\n' % str(now())
#         # time.sleep(2)
#
# REDIS_CONN.set('12345678910',json.dumps({'msg':123,'detail':456}),ex=5)

# print(type(0.2))

# l = [1,2,3]
# print(l[1:10])
# import datetime
# now = datetime.datetime.now()
# print(str(now.year)+"-"+str(now.month)+"-"+str(now.day))
# print(time.strftime("%Y-%m-%d", time.localtime()))

# condition = True
# print(2 if condition else 1/0)
# print(condition)
# Acceptor_or_pmje = 0.2
# print(str(Acceptor_or_pmje).isdigit())

# {'jj': '竞价', 'ykj': '一口价', 'llj': '利率价'}
# {'sh': '审核中', 'sj': '上架售卖', 'gj': '改价', 'xj': '已下架', 'indeal': '正在交易', 'deal': '交易完成', 'reject': '审核不通过'}
# status_1 = (("jj", "竞价"), ("ykj", "一口价"), ("llj", "利率价"))
# print(dict(status_1))

# IP = socket.gethostbyname(socket.getfqdn(socket.gethostname()))
# print(IP)

# from datetime import datetime
# text = '2012-09-20'
# y = datetime.strptime(text, '%Y-%m-%d')
# z = datetime.now()
# diff = z - y
# print(diff)

# print(dict((("sh", "审核中"), ("sj", "上架售卖"), ('gj', '改价'), ("xj", "已下架"), ('indeal', '正在交易'), ("deal", "交易完成"),
#                  ('reject', '审核不通过'))))
all_dd_status = [{"name": "审核中", "val": "sh"}, {"name": "已上架", "val": "sj"},
                 {"name": "已下架", "val": "xj"}, {"name": "交易中", "val": "indeal"},
                 {"name": "交易完成", "val": "deal"}, {"name": "审核未通过", "val": "reject"}]

all_dd_status1 = [{"name": "重新上架", "val": "rsj"}, {"name": "交易完成", "val": "deal"}]
