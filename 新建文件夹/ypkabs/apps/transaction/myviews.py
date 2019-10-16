
import datetime

from django.utils.timezone import now

from django.conf import settings
from django.http.response import JsonResponse
# from eslcampus.settings import REDIS_CONN
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from transaction.models import Piaoju, PiaojuOrder

from utils.pagination import Pagination

from utils.menu import TICKET_MENU


class MyTicket(APIView):
    all_dd_status = [{"name": "审核中", "val": "sh"}, {"name": "已上架", "val": "sj"},
                     {"name": "已下架", "val": "xj"}, {"name": "交易中", "val": "indeal"},
                     {"name": "交易完成", "val": "deal"}, {"name": "审核未通过", "val": "reject"}]

    all_dd_status1 = [{"name": "重新上架", "val": "rsj"}, {"name": "交易完成", "val": "deal"}]

    status_1 = {'sh': '审核中', 'rsj': '重新上架', 'sj': '上架售卖', 'gj': '改价', 'xj': '已下架', 'indeal': '正在交易', 'deal': '交易完成',
                'reject': '审核不通过'}

    status_2 = {'jj': '竞价', 'ykj': '一口价', 'llj': '利率价'}

    # now = datetime.datetime.now()
    now_date = now()

    def post(self, request):
        content = {}

        now_date = now()
        min_date = request.data.get("min_date", '')
        max_date = request.data.get("max_date", '')
        dd_style = request.data.get("dd_style", '')
        Acceptor_or_pmje = request.data.get("Acceptor_or_pmje", '')
        page_num = request.data.get("page_num", 1)  # 页数
        ticket_status = request.data.get("ticket_status", "today_piaoju")  # 票据状态

        if ticket_status == "today_piaoju":  # 当日票据
            if min_date == "" and max_date == "" and dd_style == "" and Acceptor_or_pmje == "":
                return self.not_all(request, now_date, content, page_num)

            if max_date == "" and dd_style == "" and Acceptor_or_pmje == "":
                return self.min_data(request, now_date, min_date, content, page_num)

            if min_date == "" and dd_style == "" and Acceptor_or_pmje == "":
                return self.max_data(request, now_date, max_date, content, page_num)

            if min_date == "" and max_date == "" and Acceptor_or_pmje == "":
                return self.dd_style(request, now_date, dd_style, content, page_num)

            if min_date == "" and max_date == "" and dd_style == "":
                print("我要走这里")
                return self.Acceptor_or_pmje(request, now_date, Acceptor_or_pmje, content, page_num)

            if min_date == "" and max_date == "":
                return self.not_min_max(request, now_date, dd_style, Acceptor_or_pmje, content, page_num)

            if min_date == "" and dd_style == "":
                return self.not_min_dd_style(request, now_date, max_date, Acceptor_or_pmje, content, page_num)

            if min_date == "" and Acceptor_or_pmje == "":
                return self.not_min_Acceptor_or_pmje(request, now_date, max_date, dd_style, content, page_num)

            if max_date == "" and dd_style == "":
                return self.not_max_dd_style(request, now_date, min_date, Acceptor_or_pmje, content, page_num)

            if max_date == "" and Acceptor_or_pmje == "":
                return self.not_max_Acceptor_or_pmje(request, now_date, min_date, dd_style, content, page_num)

            if dd_style == "" and Acceptor_or_pmje == "":
                return self.not_dd_style_Acceptor_or_pmje(request, now_date, max_date, min_date, content, page_num)

            if min_date == "":
                return self.not_min_data(request, now_date, max_date, dd_style, Acceptor_or_pmje, content, page_num)

            if max_date == "":
                return self.not_max_data(request, now_date, min_date, dd_style, Acceptor_or_pmje, content, page_num)

            if dd_style == "":
                return self.not_dd_style(request, now_date, max_date, min_date, Acceptor_or_pmje, content, page_num)

            if Acceptor_or_pmje == "":
                return self.not_Acceptor_or_pmje(request, now_date, min_date, max_date, dd_style, content, page_num)

        elif ticket_status == "history_piaoju":  # 我的历史票据

            if min_date == "" and max_date == "" and dd_style == "" and Acceptor_or_pmje == "":
                return self.not_all1(request, content, page_num)

            if max_date == "" and dd_style == "" and Acceptor_or_pmje == "":
                return self.min_data1(request, min_date, content, page_num)

            if min_date == "" and dd_style == "" and Acceptor_or_pmje == "":
                return self.max_data1(request, max_date, content, page_num)

            if min_date == "" and max_date == "" and Acceptor_or_pmje == "":
                return self.dd_style1(request, dd_style, content, page_num)

            if min_date == "" and max_date == "" and dd_style == "":
                print('我要走这里')
                return self.Acceptor_or_pmje1(request, Acceptor_or_pmje, content, page_num)

            if min_date == "" and max_date == "":
                return self.not_min_max1(request, dd_style, Acceptor_or_pmje, content, page_num)

            if min_date == "" and dd_style == "":
                return self.not_min_dd_style1(request, max_date, Acceptor_or_pmje, content, page_num)

            if min_date == "" and Acceptor_or_pmje == "":
                return self.not_min_Acceptor_or_pmje1(request, max_date, dd_style, content, page_num)

            if max_date == "" and dd_style == "":
                return self.not_max_dd_style1(request, min_date, Acceptor_or_pmje, content, page_num)

            if max_date == "" and Acceptor_or_pmje == "":
                return self.not_max_Acceptor_or_pmje1(request, min_date, dd_style, content, page_num)

            if dd_style == "" and Acceptor_or_pmje == "":
                return self.not_dd_style_Acceptor_or_pmje1(request, max_date, min_date, content, page_num)

            if min_date == "":
                return self.not_min_data1(request, max_date, dd_style, Acceptor_or_pmje, content, page_num)

            if max_date == "":
                return self.not_max_data1(request, min_date, dd_style, Acceptor_or_pmje, content, page_num)

            if dd_style == "":
                return self.not_dd_style1(request, max_date, min_date, Acceptor_or_pmje, content, page_num)

            if Acceptor_or_pmje == "":
                return self.not_Acceptor_or_pmje1(request, min_date, max_date, dd_style, content, page_num)


    ########

    def not_all(self, request, now_date, content, page_num):

        print("走这里了吗")
        print("weisha")
        all_data = Piaoju.objects.filter(fabu_user=request.user.username, date_add__contains=now_date).values(
            "date_add", "piaohao",
            "pm_amount",
            "bank", "date_daoqi",
            "jiaoyi_type", "jiaoyi_jiage",
            "pic1", "number_total",
            "status", "jiaoyi_lilv", "tzdays", "id")

        print(all_data)
        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_data(content['data'])
        return JsonResponse({'error_code': 1, "page_total": all_count,
                             "all_dd_status": self.all_dd_status, "content": res[page.start:page.end]},
                            safe=False)

    def not_min_data(self, request, now_date, max_date, dd_style, Acceptor_or_pmje, content, page_num):
        if Acceptor_or_pmje.isdigit():
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                             date_add=now_date, date_add__lte=max_date,
                                             status__contains=dd_style,
                                             pm_amount__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                          "pm_amount",
                                                                                          "bank", "date_daoqi",
                                                                                          "jiaoyi_type", "jiaoyi_jiage",
                                                                                          "pic1", "number_total",
                                                                                          "status", "jiaoyi_lilv",
                                                                                          "tzdays", "id")

        else:
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                             date_add=now_date, date_add__lte=max_date,
                                             status__contains=dd_style,
                                             bank__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                     "pm_amount",
                                                                                     "bank", "date_daoqi",
                                                                                     "jiaoyi_type", "jiaoyi_jiage",
                                                                                     "pic1", "number_total",
                                                                                     "status", "jiaoyi_lilv", "tzdays",
                                                                                     "id")

        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_data(content['data'])
        return JsonResponse({'error_code': 1, "page_total": all_count,"all_dd_status": self.all_dd_status, "content": res[page.start:page.end]},
                            safe=False)

    def not_max_data(self, request, now_date, min_date, dd_style, Acceptor_or_pmje, content, page_num):
        if Acceptor_or_pmje.isdigit():
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                             date_add=now_date, date_add__gte=min_date,
                                             status__contains=dd_style,
                                             pm_amount__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                          "pm_amount",
                                                                                          "bank", "date_daoqi",
                                                                                          "jiaoyi_type", "jiaoyi_jiage",
                                                                                          "pic1", "number_total",
                                                                                          "status", "jiaoyi_lilv",
                                                                                          "tzdays", "id")

        else:
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                             date_add=now_date, date_add__gte=min_date,
                                             status__contains=dd_style,
                                             bank__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                     "pm_amount",
                                                                                     "bank", "date_daoqi",
                                                                                     "jiaoyi_type", "jiaoyi_jiage",
                                                                                     "pic1", "number_total",
                                                                                     "status", "jiaoyi_lilv", "tzdays",
                                                                                     "id")
        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_data(content['data'])
        return JsonResponse({'error_code': 1, "page_total": all_count,"all_dd_status": self.all_dd_status, "content": res[page.start:page.end]},
                            safe=False)

    def not_dd_style(self, request, now_date, max_date, min_date, Acceptor_or_pmje, content, page_num):
        if Acceptor_or_pmje.isdigit():
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                             date_add=now_date, date_add__lte=max_date,
                                             date_add__gte=min_date,
                                             pm_amount__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                          "pm_amount",
                                                                                          "bank", "date_daoqi",
                                                                                          "jiaoyi_type", "jiaoyi_jiage",
                                                                                          "pic1", "number_total",
                                                                                          "status", "jiaoyi_lilv",
                                                                                          "tzdays", "id")

        else:
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                             date_add=now_date, date_add__lte=max_date,
                                             date_add__gte=min_date,
                                             bank__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                     "pm_amount",
                                                                                     "bank", "date_daoqi",
                                                                                     "jiaoyi_type", "jiaoyi_jiage",
                                                                                     "pic1", "number_total",
                                                                                     "status", "jiaoyi_lilv", "tzdays",
                                                                                     "id")
        content['data'] = list(all_data)
        print("<><><><>",all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_data(content['data'])
        return JsonResponse({'error_code': 1, "page_total": all_count, "all_dd_status": self.all_dd_status,"content": res[page.start:page.end]},
                            safe=False)

    def not_Acceptor_or_pmje(self, request, now_date, min_date, max_date, dd_style, content, page_num):

        all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                         date_add__gte=min_date,
                                         date_add=now_date, date_add__lte=max_date,
                                         status__contains=dd_style,
                                         ).values("date_add", "piaohao",
                                                  "pm_amount",
                                                  "bank", "date_daoqi",
                                                  "jiaoyi_type", "jiaoyi_jiage",
                                                  "pic1", "number_total",
                                                  "status", "jiaoyi_lilv", "tzdays", "id")
        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_data(content['data'])
        return JsonResponse({'error_code': 1,"all_dd_status": self.all_dd_status, "page_total": all_count, "content": res[page.start:page.end]},
                            safe=False)

    def not_min_max(self, request, now_date, dd_style, Acceptor_or_pmje, content, page_num):
        if Acceptor_or_pmje.isdigit():
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                             date_add=now_date,
                                             status__contains=dd_style,
                                             pm_amount__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                          "pm_amount",
                                                                                          "bank", "date_daoqi",
                                                                                          "jiaoyi_type", "jiaoyi_jiage",
                                                                                          "pic1", "number_total",
                                                                                          "status", "jiaoyi_lilv",
                                                                                          "tzdays", "id")
        else:
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                             date_add=now_date,
                                             status__contains=dd_style,
                                             bank__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                     "pm_amount",
                                                                                     "bank", "date_daoqi",
                                                                                     "jiaoyi_type", "jiaoyi_jiage",
                                                                                     "pic1", "number_total",
                                                                                     "status", "jiaoyi_lilv", "tzdays",
                                                                                     "id")
        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_data(content['data'])
        return JsonResponse({'error_code': 1,"all_dd_status": self.all_dd_status, "page_total": all_count, "content": res[page.start:page.end]},
                            safe=False)

    def not_min_dd_style(self, request, now_date, max_date, Acceptor_or_pmje, content, page_num):
        if Acceptor_or_pmje.isdigit():
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                             date_add=now_date, date_add__lte=max_date,
                                             pm_amount__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                          "pm_amount",
                                                                                          "bank", "date_daoqi",
                                                                                          "jiaoyi_type", "jiaoyi_jiage",
                                                                                          "pic1", "number_total",
                                                                                          "status", "jiaoyi_lilv",
                                                                                          "tzdays", "id")
        else:
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                             date_add=now_date,
                                             bank__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                     "pm_amount",
                                                                                     "bank", "date_daoqi",
                                                                                     "jiaoyi_type", "jiaoyi_jiage",
                                                                                     "pic1", "number_total",
                                                                                     "status", "jiaoyi_lilv", "tzdays",
                                                                                     "id")
        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_data(content['data'])
        return JsonResponse({'error_code': 1,"all_dd_status": self.all_dd_status, "page_total": all_count, "content": res[page.start:page.end]},
                            safe=False)

    def not_min_Acceptor_or_pmje(self, request, now_date, max_date, dd_style, content, page_num):

        all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                         date_add=now_date, date_add__lte=max_date,
                                         status__contains=dd_style,
                                         ).values("date_add", "piaohao",
                                                  "pm_amount",
                                                  "bank", "date_daoqi",
                                                  "jiaoyi_type", "jiaoyi_jiage",
                                                  "pic1", "number_total",
                                                  "status", "jiaoyi_lilv", "tzdays", "id")

        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_data(content['data'])
        return JsonResponse({'error_code': 1,"all_dd_status": self.all_dd_status, "page_total": all_count, "content": res[page.start:page.end]},
                            safe=False)

    def not_max_dd_style(self, request, now_date, min_date, Acceptor_or_pmje, content, page_num):
        if Acceptor_or_pmje.isdigit():
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                             date_add=now_date, date_add__gte=min_date,
                                             pm_amount__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                          "pm_amount",
                                                                                          "bank", "date_daoqi",
                                                                                          "jiaoyi_type", "jiaoyi_jiage",
                                                                                          "pic1", "number_total",
                                                                                          "status", "jiaoyi_lilv",
                                                                                          "tzdays", "id")

        else:
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                             date_add=now_date, date_add__gte=min_date,
                                             bank__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                     "pm_amount",
                                                                                     "bank", "date_daoqi",
                                                                                     "jiaoyi_type", "jiaoyi_jiage",
                                                                                     "pic1", "number_total",
                                                                                     "status", "jiaoyi_lilv", "tzdays",
                                                                                     "id")
        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count())
        all_count = all_data.count()

        res = self.handle_data(content['data'])
        return JsonResponse({'error_code': 1,"all_dd_status": self.all_dd_status, "page_total": all_count, "content": res[page.start:page.end]},
                            safe=False)

    def not_max_Acceptor_or_pmje(self, request, now_date, min_date, dd_style, content, page_num):

        all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                         date_add=now_date, date_add__gte=min_date,
                                         status__contains=dd_style,
                                         ).values("date_add", "piaohao",
                                                  "pm_amount",
                                                  "bank", "date_daoqi",
                                                  "jiaoyi_type", "jiaoyi_jiage",
                                                  "pic1", "number_total",
                                                  "status", "jiaoyi_lilv", "tzdays", "id")
        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_data(content['data'])
        return JsonResponse({'error_code': 1,"all_dd_status": self.all_dd_status, "page_total": all_count, "content": res[page.start:page.end]},
                            safe=False)

    def not_dd_style_Acceptor_or_pmje(self, request, now_date, max_date, min_date, content, page_num):
        all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                         date_add=now_date, date_add__lte=max_date,
                                         date_add__gte=min_date,
                                         ).values("date_add", "piaohao",
                                                  "pm_amount",
                                                  "bank", "date_daoqi",
                                                  "jiaoyi_type", "jiaoyi_jiage",
                                                  "pic1", "number_total",
                                                  "status", "jiaoyi_lilv", "tzdays", "id")
        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_data(content['data'])
        return JsonResponse({'error_code': 1,"all_dd_status": self.all_dd_status, "page_total": all_count, "content": res[page.start:page.end]},
                            safe=False)

    def min_data(self, request, now_date, min_date, content, page_num):

        all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                         date_add=now_date, date_add__gte=min_date).values("date_add", "piaohao",
                                                                                           "pm_amount",
                                                                                           "bank", "date_daoqi",
                                                                                           "jiaoyi_type",
                                                                                           "jiaoyi_jiage",
                                                                                           "pic1", "number_total",
                                                                                           "status", "jiaoyi_lilv",
                                                                                           "tzdays", "id")
        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_data(content['data'])
        return JsonResponse({'error_code': 1,"all_dd_status": self.all_dd_status, "page_total": all_count, "content": res[page.start:page.end]},
                            safe=False)

    def max_data(self, request, now_date, max_date, content, page_num):
        all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                         date_add=now_date, date_add__lte=max_date).values("date_add", "piaohao",
                                                                                           "pm_amount",
                                                                                           "bank", "date_daoqi",
                                                                                           "jiaoyi_type",
                                                                                           "jiaoyi_jiage",
                                                                                           "pic1", "number_total",
                                                                                           "status", "jiaoyi_lilv",
                                                                                           "tzdays", "id")
        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_data(content['data'])
        return JsonResponse({'error_code': 1,"all_dd_status": self.all_dd_status, "page_total": all_count, "content": res[page.start:page.end]},
                            safe=False)

    def dd_style(self, request, now_date, dd_style, content, page_num):
        print(dd_style)
        print(now_date)
        print(request.user.username)
        all_data = Piaoju.objects.filter(fabu_user=request.user.username,date_add__gt=now_date,status=dd_style).values("date_add", "piaohao",
                                                                                                "pm_amount",
                                                                                                "bank", "date_daoqi",
                                                                                                "jiaoyi_type",
                                                                                                "jiaoyi_jiage",
                                                                                                "pic1", "number_total",
                                                                                                "status", "jiaoyi_lilv",
                                                                                                "tzdays", "id")

        content['data'] = list(all_data)
        print("<><>",all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_data(content['data'])
        return JsonResponse({'error_code': 1,"all_dd_status": self.all_dd_status, "page_total": all_count, "content": res[page.start:page.end]},
                            safe=False)

    def Acceptor_or_pmje(self, request, now_date, Acceptor_or_pmje, content, page_num):
        print(12332111223300000)
        if Acceptor_or_pmje.isdigit():
            all_data = Piaoju.objects.filter(fabu_user=request.user.username, date_add=now_date,
                                             pm_amount__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                          "pm_amount",
                                                                                          "bank", "date_daoqi",
                                                                                          "jiaoyi_type", "jiaoyi_jiage",
                                                                                          "pic1", "number_total",
                                                                                          "status", "jiaoyi_lilv",
                                                                                          "tzdays", "id")

        else:
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                             bank__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                     "pm_amount",
                                                                                     "bank", "date_daoqi",
                                                                                     "jiaoyi_type", "jiaoyi_jiage",
                                                                                     "pic1", "number_total",
                                                                                     "status", "jiaoyi_lilv", "tzdays",
                                                                                     "id")

        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count())
        all_count = all_data.count()

        res = self.handle_data(content['data'])
        return JsonResponse({'error_code': 1,"all_dd_status": self.all_dd_status, "page_total": all_count, "content": res[page.start:page.end]},
                            safe=False)

    ########

    def not_all1(self, request, content, page_num):
        all_data = Piaoju.objects.filter(fabu_user=request.user.username).values("date_add", "piaohao",
                                                                                 "pm_amount",
                                                                                 "bank", "date_daoqi",
                                                                                 "jiaoyi_type", "jiaoyi_jiage",
                                                                                 "pic1", "number_total",
                                                                                 "status", "jiaoyi_lilv", "tzdays",
                                                                                 "id")

        print(all_data)
        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_history_data(content['data'])
        return JsonResponse({'error_code': 1, "page_total": all_count, "all_dd_status": self.all_dd_status1,
                             "content": res[page.start:page.end]})

    # ser_obj = MyTicketSerializer(all_data,many=True)
    # gj_list = []
    # normal_list = []
    #
    # for i in ser_obj.data:
    #     # print(i)
    #     if i.get('status') == 'sj' and i.get('fabu_user') == request.user.username:
    #         i['status'] = 'gj'
    #         # i.pop('piaohao')
    #         i.pop('fabu_user')
    #         gj_list.append(i)
    #     else:
    #         normal_list.append(i)
    # return Response({'error_code': 1, "content": gj_list + normal_list})

    def not_min_data1(self, request, max_date, dd_style, Acceptor_or_pmje, content, page_num):
        print(max_date, dd_style, Acceptor_or_pmje, content, page_num)

        if Acceptor_or_pmje.isdigit():

            all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                             date_add__lte=max_date,
                                             status__contains=dd_style,
                                             pm_amount__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                          "pm_amount",
                                                                                          "bank", "date_daoqi",
                                                                                          "jiaoyi_type", "jiaoyi_jiage",
                                                                                          "pic1", "number_total",
                                                                                          "status", "jiaoyi_lilv",
                                                                                          "tzdays", "id")

        else:
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                             date_add__lte=max_date,
                                             status__contains=dd_style,
                                             bank__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                     "pm_amount",
                                                                                     "bank", "date_daoqi",
                                                                                     "jiaoyi_type", "jiaoyi_jiage",
                                                                                     "pic1", "number_total",
                                                                                     "status", "jiaoyi_lilv", "tzdays",
                                                                                     "id")
        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_history_data(content['data'])
        return JsonResponse({'error_code': 1, "page_total": all_count, "all_dd_status": self.all_dd_status1,"content": res[page.start:page.end]},
                            safe=False)

    def not_max_data1(self, request, min_date, dd_style, Acceptor_or_pmje, content, page_num):
        if Acceptor_or_pmje.isdigit():
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                             date_add__gte=min_date,
                                             status__contains=dd_style,
                                             pm_amount__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                          "pm_amount",
                                                                                          "bank", "date_daoqi",
                                                                                          "jiaoyi_type", "jiaoyi_jiage",
                                                                                          "pic1", "number_total",
                                                                                          "status", "jiaoyi_lilv",
                                                                                          "tzdays", "id")

        else:
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                             date_add__gte=min_date,
                                             status__contains=dd_style,
                                             bank__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                     "pm_amount",
                                                                                     "bank", "date_daoqi",
                                                                                     "jiaoyi_type", "jiaoyi_jiage",
                                                                                     "pic1", "number_total",
                                                                                     "status", "jiaoyi_lilv", "tzdays",
                                                                                     "id")

        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_history_data(content['data'])
        return JsonResponse({'error_code': 1, "page_total": all_count,"all_dd_status": self.all_dd_status1, "content": res[page.start:page.end]},
                            safe=False)

    def not_dd_style1(self, request, max_date, min_date, Acceptor_or_pmje, content, page_num):
        if Acceptor_or_pmje.isdigit():
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                             date_add__lte=max_date,
                                             date_add__gte=min_date,
                                             pm_amount__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                          "pm_amount",
                                                                                          "bank", "date_daoqi",
                                                                                          "jiaoyi_type", "jiaoyi_jiage",
                                                                                          "pic1", "number_total",
                                                                                          "status", "jiaoyi_lilv",
                                                                                          "tzdays", "id")

        else:
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                             date_add__lte=max_date,
                                             date_add__gte=min_date,
                                             bank__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                     "pm_amount",
                                                                                     "bank", "date_daoqi",
                                                                                     "jiaoyi_type", "jiaoyi_jiage",
                                                                                     "pic1", "number_total",
                                                                                     "status", "jiaoyi_lilv", "tzdays",
                                                                                     "id")
        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_history_data(content['data'])
        return JsonResponse({'error_code': 1,"all_dd_status": self.all_dd_status1, "page_total": all_count, "content": res[page.start:page.end]},
                            safe=False)

    def not_Acceptor_or_pmje1(self, request, min_date, max_date, dd_style, content, page_num):

        all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                         date_add__gte=min_date,
                                         date_add__lte=max_date,
                                         status__contains=dd_style,
                                         ).values("date_add", "piaohao",
                                                  "pm_amount",
                                                  "bank", "date_daoqi",
                                                  "jiaoyi_type", "jiaoyi_jiage",
                                                  "pic1", "number_total",
                                                  "status", "jiaoyi_lilv", "tzdays", "id")
        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_history_data(content['data'])
        return JsonResponse({'error_code': 1,"all_dd_status": self.all_dd_status1, "page_total": all_count, "content": res[page.start:page.end]},
                            safe=False)

    def not_min_max1(self, request, dd_style, Acceptor_or_pmje, content, page_num):
        if Acceptor_or_pmje.isdigit():
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,

                                             status__contains=dd_style,
                                             pm_amount__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                          "pm_amount",
                                                                                          "bank", "date_daoqi",
                                                                                          "jiaoyi_type", "jiaoyi_jiage",
                                                                                          "pic1", "number_total",
                                                                                          "status", "jiaoyi_lilv",
                                                                                          "tzdays", "id")
        else:
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,

                                             status__contains=dd_style,
                                             bank__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                     "pm_amount",
                                                                                     "bank", "date_daoqi",
                                                                                     "jiaoyi_type", "jiaoyi_jiage",
                                                                                     "pic1", "number_total",
                                                                                     "status", "jiaoyi_lilv", "tzdays",
                                                                                     "id")
        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_history_data(content['data'])
        return JsonResponse({'error_code': 1,"all_dd_status": self.all_dd_status1, "page_total": all_count, "content": res[page.start:page.end]},
                            safe=False)

    def not_min_dd_style1(self, request, max_date, Acceptor_or_pmje, content, page_num):
        if Acceptor_or_pmje.isdigit():
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                             date_add__lte=max_date,
                                             pm_amount__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                          "pm_amount",
                                                                                          "bank", "date_daoqi",
                                                                                          "jiaoyi_type", "jiaoyi_jiage",
                                                                                          "pic1", "number_total",
                                                                                          "status", "jiaoyi_lilv",
                                                                                          "tzdays", "id")
        else:
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,

                                             bank__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                     "pm_amount",
                                                                                     "bank", "date_daoqi",
                                                                                     "jiaoyi_type", "jiaoyi_jiage",
                                                                                     "pic1", "number_total",
                                                                                     "status", "jiaoyi_lilv", "tzdays",
                                                                                     "id")
        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_history_data(content['data'])
        return JsonResponse({'error_code': 1,"all_dd_status": self.all_dd_status1, "page_total": all_count, "content": res[page.start:page.end]},
                            safe=False)

    def not_min_Acceptor_or_pmje1(self, request, max_date, dd_style, content, page_num):

        all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                         date_add__lte=max_date,
                                         status__contains=dd_style,
                                         ).values("date_add", "piaohao",
                                                  "pm_amount",
                                                  "bank", "date_daoqi",
                                                  "jiaoyi_type", "jiaoyi_jiage",
                                                  "pic1", "number_total",
                                                  "status", "jiaoyi_lilv", "tzdays", "id")
        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_history_data(content['data'])
        return JsonResponse({'error_code': 1,"all_dd_status": self.all_dd_status1, "page_total": all_count, "content": res[page.start:page.end]},
                            safe=False)

    def not_max_dd_style1(self, request, min_date, Acceptor_or_pmje, content, page_num):
        if Acceptor_or_pmje.isdigit():
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                             date_add__gte=min_date,
                                             pm_amount__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                          "pm_amount",
                                                                                          "bank", "date_daoqi",
                                                                                          "jiaoyi_type", "jiaoyi_jiage",
                                                                                          "pic1", "number_total",
                                                                                          "status", "jiaoyi_lilv",
                                                                                          "tzdays", "id")

        else:
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                             date_add__gte=min_date,
                                             bank__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                     "pm_amount",
                                                                                     "bank", "date_daoqi",
                                                                                     "jiaoyi_type", "jiaoyi_jiage",
                                                                                     "pic1", "number_total",
                                                                                     "status", "jiaoyi_lilv", "tzdays",
                                                                                     "id")
        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_history_data(content['data'])
        return JsonResponse({'error_code': 1,"all_dd_status": self.all_dd_status1, "page_total": all_count, "content": res[page.start:page.end]},
                            safe=False)

    def not_max_Acceptor_or_pmje1(self, request, min_date, dd_style, content, page_num):

        all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                         date_add__gte=min_date,
                                         status__contains=dd_style,
                                         ).values("date_add", "piaohao",
                                                  "pm_amount",
                                                  "bank", "date_daoqi",
                                                  "jiaoyi_type", "jiaoyi_jiage",
                                                  "pic1", "number_total",
                                                  "status", "jiaoyi_lilv", "tzdays", "id")
        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_history_data(content['data'])
        return JsonResponse({'error_code': 1,"all_dd_status": self.all_dd_status1, "page_total": all_count, "content": res[page.start:page.end]},
                            safe=False)

    def not_dd_style_Acceptor_or_pmje1(self, request, max_date, min_date, content, page_num):
        all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                         date_add__lte=max_date,
                                         date_add__gte=min_date,
                                         ).values("date_add", "piaohao",
                                                  "pm_amount",
                                                  "bank", "date_daoqi",
                                                  "jiaoyi_type", "jiaoyi_jiage",
                                                  "pic1", "number_total",
                                                  "status", "jiaoyi_lilv", "tzdays", "id")
        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_history_data(content['data'])
        return JsonResponse({'error_code': 1,"all_dd_status": self.all_dd_status1, "page_total": all_count, "content": res[page.start:page.end]},
                            safe=False)

    def min_data1(self, request, min_date, content, page_num):

        all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                         date_add__gte=min_date).values("date_add", "piaohao",
                                                                        "pm_amount",
                                                                        "bank", "date_daoqi",
                                                                        "jiaoyi_type", "jiaoyi_jiage",
                                                                        "pic1", "number_total",
                                                                        "status", "jiaoyi_lilv", "tzdays", "id")
        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_history_data(content['data'])
        return JsonResponse({'error_code': 1,"all_dd_status": self.all_dd_status1, "page_total": all_count, "content": res[page.start:page.end]},
                            safe=False)

    def max_data1(self, request, max_date, content, page_num):
        all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                         date_add__lte=max_date).values("date_add", "piaohao",
                                                                        "pm_amount",
                                                                        "bank", "date_daoqi",
                                                                        "jiaoyi_type", "jiaoyi_jiage",
                                                                        "pic1", "number_total",
                                                                        "status", "jiaoyi_lilv", "tzdays", "id")
        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_history_data(content['data'])
        return JsonResponse({'error_code': 1,"all_dd_status": self.all_dd_status1, "page_total": all_count, "content": res[page.start:page.end]},
                            safe=False)

    def dd_style1(self, request, dd_style, content, page_num):
        all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                         status__contains=dd_style, ).values("date_add", "piaohao",
                                                                             "pm_amount",
                                                                             "bank", "date_daoqi",
                                                                             "jiaoyi_type", "jiaoyi_jiage",
                                                                             "pic1", "number_total",
                                                                             "status", "jiaoyi_lilv", "tzdays", "id")
        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_history_data(content['data'])
        return JsonResponse({'error_code': 1,"all_dd_status": self.all_dd_status1, "page_total": all_count, "content": res[page.start:page.end]}, safe=False)

    def Acceptor_or_pmje1(self, request, Acceptor_or_pmje, content, page_num):
        if Acceptor_or_pmje.isdigit():
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                             pm_amount__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                          "pm_amount",
                                                                                          "bank", "date_daoqi",
                                                                                          "jiaoyi_type", "jiaoyi_jiage",
                                                                                          "pic1", "number_total",
                                                                                          "status", "jiaoyi_lilv",
                                                                                          "tzdays", "id")

        else:
            all_data = Piaoju.objects.filter(fabu_user=request.user.username,
                                             bank__contains=Acceptor_or_pmje).values("date_add", "piaohao",
                                                                                     "pm_amount",
                                                                                     "bank", "date_daoqi",
                                                                                     "jiaoyi_type", "jiaoyi_jiage",
                                                                                     "pic1", "number_total",
                                                                                     "status", "jiaoyi_lilv", "tzdays",
                                                                                     "id")

        print(all_data)
        content['data'] = list(all_data)
        page = Pagination(page_num, all_data.count(), )
        all_count = all_data.count()

        res = self.handle_history_data(content['data'])

        return JsonResponse({'error_code': 1,"all_dd_status": self.all_dd_status1, "page_total": all_count, "content": res[page.start:page.end]})

    # all_dd_status = [{"name": "审核中", "val": "sh"}, {"name": "已上架", "val": "sj"},
    #                  {"name": "已下架", "val": "xj"}, {"name": "交易中", "val": "indeal"},
    #                  {"name": "交易完成", "val": "deal"}, {"name": "审核未通过", "val": "reject"}]
    def handle_data(self, data_list):
        status_1 = {'sh': '审核中', 'rsj': '重新上架', 'sj': '已上架', 'gj': '改价', 'xj': '已下架', 'indeal': '交易中', 'deal': '交易完成',
                    'reject': '审核未通过'}
        status_2 = {'jj': '竞价', 'ykj': '一口价', 'llj': '利率价'}

        for i in data_list:
            i['piaohao'] = i['piaohao'][-6::]
            i['jiaoyi_type'] = self.status_2[i["jiaoyi_type"]]
            i['status_1'] = self.status_1[i['status']]
            i['pic1'] = f"http://{settings.IP}:9999/media/{i['pic1']}"
            d1 = datetime.datetime.strptime(i['date_daoqi'].strftime('%Y-%m-%d'), "%Y-%m-%d")
            d2 = datetime.datetime.strptime(self.now_date, "%Y-%m-%d")

            i['remain_days'] = str(d1 - d2).split()[0]
        print(data_list)
        return data_list

    def handle_history_data(self, data_list):

        for i in data_list:
            i['piaohao'] = i['piaohao'][-6::]
            i['jiaoyi_type'] = self.status_2[i["jiaoyi_type"]]
            i['status_1'] = self.status_1[i['status']]
            i['pic1'] = f"http://{settings.IP}:9999/media/{i['pic1']}"
            d1 = datetime.datetime.strptime(i['date_daoqi'].strftime('%Y-%m-%d'), "%Y-%m-%d")
            d2 = datetime.datetime.strptime(self.now_date, "%Y-%m-%d")
            i['remain_days'] = int(str(d1 - d2).split()[0])

        print(data_list)
        return data_list


class TicketsMenu(APIView):
    '''
    票据菜单
    '''

    def post(self, request):
        return Response({'menu': TICKET_MENU, 'error_code': 1}, status=status.HTTP_200_OK,
                        content_type='application/json')


class XJticket(APIView):
    '''
    下架票据
    '''

    def post(self, request):
        print("我要下架了")
        id = request.data.get("id")
        update_pj = Piaoju.objects.filter(fabu_user=request.user.username, id=id).update(status="xj")
        if update_pj:
            return JsonResponse({'error_code': 1})
        else:
            return JsonResponse({'error_code': 1000, "detail": "抱歉，并没有查询到该票据！"})


class SJticket(APIView):
    '''
    上架票据
    '''
    nows = datetime.datetime.now()
    now_date = str(nows.year) + "-" + str(nows.month) + "-" + str(nows.day)

    def post(self, request):
        id = request.data.get("id")
        obj = Piaoju.objects.filter(fabu_user=request.user.username, id=id)
        # print(obj.values("status"))
        update_pj = Piaoju.objects.filter(fabu_user=request.user.username, id=id).update(status="sj", date_add=now())

        if update_pj:
            return JsonResponse({'error_code': 1})
        else:
            return JsonResponse({'error_code': 1000, "detail": "抱歉，并没有查询到该票据！"})


class Delticket(APIView):
    '''
    删除票据
    '''

    def post(self, request):
        print("我要删除数据了")
        id = request.data.get("id")
        del_pj = Piaoju.objects.filter(fabu_user=request.user.username, id=id).delete()
        if del_pj:
            return JsonResponse({'error_code': 1})
        else:
            return JsonResponse({'error_code': 1000, "detail": "抱歉，并没有查询到该票据, 删除失败！"})
