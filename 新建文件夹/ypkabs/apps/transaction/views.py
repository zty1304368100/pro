# Create your views here.
import base64
import copy
import datetime
import hashlib
import os, logging
from eslcampus.settings import REDIS_CONN
from django.conf import settings
from django.db.models import Q
from django.views import View
from django.shortcuts import render,HttpResponse,redirect
from django.utils.timezone import now
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from transaction.calculate import yikoujia2lilv, lilv2yikoujia
from transaction.models import BankAccount, Piaoju, PiaojuOrder
from transaction.serializers import TicketsMallSerializer, TicketsDetailSerializer, TicketsOrderSerializer
from users.auth import DefaultTAuth
from users.permission import SuperuserPermission

from utils import image_compress, baiduocr, msgremind
from utils.menu import MENU, UPLOAD_MENU, ORDER_MENU
import time
from uuid import uuid4

from utils.scripts import save_notice, getTotalJindou, get_order_fee, reach_buyer_processing_order_limit

logging.basicConfig()
logger = logging.getLogger("django")


class TestView(APIView):
    '''
    测试视图
    '''
    # authentication_classes = [] 重写认证列表,为空不执行认证操作,在settings里的全局认证失效.
    authentication_classes = []

    # authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    # permission_classes = [SuperuserPermission]

    # permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({'1': {'msg': "认证后才能看到此内容"}, 'status': '2'})


class UploadMenuView(APIView):
    '''
    银票商票上传菜单请求接口,票据所在户列表
    '''

    def post(self, request):
        try:
            acct_list = BankAccount.objects.filter(gongsi_id=request.user.gongsi_id, acct_type=0)
        except BankAccount.DoesNotExist:
            return Response({'error_code': 1001, 'detail': '票据所在户不存在,请先添加票据所在户'})
        else:
            bankaccount_belong = list(acct_list.values('id', 'bank_name', 'bank_no', 'account'))
            UPLOAD_MENU['bankaccount_belong'] = bankaccount_belong
            return Response({'menu': UPLOAD_MENU, 'error_code': 1}, status=status.HTTP_200_OK,
                            content_type='application/json')


class SearchMenuView(APIView):
    '''
    票据大厅搜索菜单列表
    '''
    authentication_classes = []

    def post(self, request):
        return Response({'menu': MENU, 'error_code': 1}, status=status.HTTP_200_OK, content_type='application/json')


class OrderMenuView(APIView):
    '''
    搜索菜单列表
    '''
    authentication_classes = []

    def post(self, request):
        return Response({'menu': ORDER_MENU, 'error_code': 1}, status=status.HTTP_200_OK, content_type='application/json')


class TicketsMallView(APIView):
    '''
    票据大厅视图
    '''
    authentication_classes = []

    def post(self, request):
        '''
        :param:request.data
        {
            'order_status':'all',
            # 筛选字段
            'jiaoyi_type':'all','ykj'，'jj'，'llj'
            'accepter':'all',
            'piaoju_type':'all',
            'flaw_type':'all','no','cf'
            # 区间字段以及筛选条件
            'date_due':'all','0-10'，'10-50'，'50-100'，'100-00'
            'pm_amount':'all','0-10'，'10-50'，'50-100'，'100-00'
            'min_lilv' : '1',   收票利率
            'max_lilv' : '10',
            'shiwanfee' : '200', 每十万手续费
            'min_date' : '1',    到期日多少天之内到期
            'max_date' : '10',
            'min_amount' : '1',  票面金额区间
            'max_amount' : '10',
            # 排序有关字段
            'current_page':'1',
            'sort':'up'/'down',
            'sort_field':'jiaoyi_type',
            'search_field':'', 模糊搜索字段
        }
        :return:Response({'ticket': ser_obj.data})
        '''
        page_number = 15
        if request._request.META.get('HTTP_TOKEN'):
            request.user, request.token = DefaultTAuth().authenticate(request)
        # print(request.user)
        # print(request.data)
        # print(request.FILES)
        # query_item = dict(request.data)
        # print(type(request.data))
        query_dict = request.data

        # print(query_item.get('username'))
        # username = query_dict.pop('username')
        # print(username)
        # print(query_dict)
        # 筛选字段
        filter_dict = {}
        if query_dict.get('order_status', 'all') != 'all':
            filter_dict['status'] = query_dict.get('order_status', 'all')
        if query_dict.get('jiaoyi_type', 'all') != 'all':
            filter_dict['jiaoyi_type'] = query_dict.get('jiaoyi_type', 'all')
        if query_dict.get('piaoju_type', 'all') != 'all':
            filter_dict['piaoju_type'] = query_dict.get('piaoju_type', 'all')
        if query_dict.get('flaw_type', 'all') != 'all':
            filter_dict['flaw_type'] = query_dict.get('flaw_type', 'all')
        if query_dict.get('accepter', 'all') != 'all':
            filter_dict['accepter'] = query_dict.get('accepter', 'all')
        if query_dict.get('qiye_category', 'all') != 'all':
            filter_dict['qiye_category'] = query_dict.get('qiye_category', 'all')
        if query_dict.get('qiye_name', 'all') != 'all':
            filter_dict['qiye_name'] = query_dict.get('qiye_name', 'all')
        if query_dict.get('piliang', 'all') != 'all':
            if query_dict.get('piliang', 'all') == "0":
                filter_dict['piliang'] = False
            elif query_dict.get('piliang', 'all') == "1":
                filter_dict['piliang'] = True

        # 区间筛选
        date_due = query_dict.get('date_due', 'all')
        pm_amount = query_dict.get('pm_amount', 'all')
        # min_lilv = query_dict.get('min_lilv','')
        jiaoyi_min_lilv = query_dict.get('min_lilv','')
        jiaoyi_max_lilv = query_dict.get('max_lilv','')
        shiwanfee = query_dict.get('shiwanfee', '')
        min_date_put = query_dict.get('min_date', '')
        max_date_put = query_dict.get('max_date', '')
        min_amount = query_dict.get('min_amount', '')
        max_amount = query_dict.get('max_amount', '')
        # 到期日不是默认的all也不是在最后输入的时候将min_date跟max_date分离为int的天数.
        min_date = 0
        max_date = 0
        if date_due != 'all' and date_due != '' and min_date_put == '' and max_date_put == '':
            min_date = int(date_due.split('-')[0])
            max_date = date_due.split('-')[1]
        if pm_amount != 'all' and pm_amount != '' and min_amount == '' and max_amount == '':
            min_amount = float(pm_amount.split('-')[0])
            max_amount = pm_amount.split('-')[1]

        # 排序相关字段
        current_page = int(query_dict.get('current_page', '1'))
        sort = query_dict.get('sort', 'down')
        sort_field = query_dict.get('sort_field', 'date_add')
        # 起始数据
        page_start = (current_page - 1) * page_number
        page_end = current_page * page_number


        # 搜索相关
        search_field = query_dict.get('search_field', '')

        queryset = Piaoju.objects.filter(Q(dingxiang=False), Q(status__in=['sj', 'deal', 'indeal'])
                                         # Q(piliang=False),Q(date_add__gte=now().date()),
                                         )
        # queryset = models.Piaoju.objects.all()

        # 开始筛选过滤
        queryset = queryset.filter(**filter_dict)  # 过滤筛选字段
        # print(filter_dict)
        # 区间搜索相关
        if shiwanfee == '':  # shiwanfee:十万手续费
            shiwanfee = 0
        if min_amount != '':
            queryset = queryset.filter(pm_amount__gte=float(min_amount))
        if max_amount != '' and max_amount != '00':
            queryset = queryset.filter(pm_amount__lte=float(max_amount))
        if jiaoyi_min_lilv != '' :
            # min_lilv = float(jiaoyi_lilv) + (float(max_amount)/100000 * shiwanfee / max_amount)
            if pm_amount != '' and pm_amount != 'all':
                min_lilv = float(jiaoyi_min_lilv) + ((float(min_amount) + float(max_amount)) / 100000 * float(shiwanfee) / (
                        float(min_amount) + float(max_amount)))
                queryset = queryset.filter(jiaoyi_lilv__gte=float(min_lilv))
            else:
                queryset = queryset.filter(jiaoyi_lilv__gte=float(jiaoyi_min_lilv))

        if jiaoyi_max_lilv != '':
            print(jiaoyi_max_lilv)
            if pm_amount != '' and pm_amount != 'all':
                max_lilv = float(jiaoyi_max_lilv) + ((float(min_amount) + float(max_amount)) / 100000 * float(shiwanfee) / (
                        float(min_amount) + float(max_amount)))
                queryset = queryset.filter(jiaoyi_lilv__lte=float(max_lilv))
            else:
                queryset = queryset.filter(jiaoyi_lilv__lte=float(jiaoyi_max_lilv))
        # 只有输入的最大最小日期为空时,才会以标签为准.min_date或者max_date不为空,这时字段为区间0-90,min_date = 0
        if min_date != '' and date_due != '' and min_date != 0:
            expire_start = datetime.datetime.now() + datetime.timedelta(days=int(min_date))
            queryset = queryset.filter(date_daoqi__gte=expire_start)
        if max_date != '00' and date_due != '' and max_date != 0:
            expire_end = datetime.datetime.now() + datetime.timedelta(days=int(max_date))
            queryset = queryset.filter(date_daoqi__lte=expire_end)
        #   这时date_due == '',优先输入的日期.
        if min_date_put != '':
            queryset = queryset.filter(date_daoqi__gte=min_date_put)
        if min_date_put != '':
            queryset = queryset.filter(date_daoqi__lt=min_date_put)
        # 模糊搜索相关
        if search_field:
            if search_field.isdigit():
                queryset = queryset.filter(piaomianjine=search_field)
            else:
                queryset = queryset.filter(bank__contains=search_field)
        # print(queryset)
        # 最终页码排序相关处理
        ticket_count = queryset.count()
        if sort == 'up':
            queryset = queryset.extra(select={'_has': 'instr(status, "sj")'}).order_by('-_has', sort_field)[
                       page_start:page_end]
            # queryset = queryset.order_by(sort_field)[page_start:page_end]
        if sort == 'down':
            queryset = queryset.extra(select={'_has': 'instr(status, "sj")'}).order_by('-_has', '-' + sort_field)[
                       page_start:page_end]
            # queryset = queryset.order_by('-' + sort_field)[page_start:page_end]

        # if queryset:
        #     for i in queryset:
        #         if i.fabu_user == request.user.username and i.status == 'sj':
        #             # print(i.id,i.fabu_user,i.status)
        #             i.status = 'gj'

        try:
            verify_state = request.user.gongsi.verify_state
        except:
            verify_state = 0
        detail = ''
        if verify_state == 0:
            detail = '请先认证!'
        if verify_state == 1:
            detail = '审核中,请耐心等待'
        elif verify_state == 2:
            detail = '认证通过,请先开通齐银e'
        elif verify_state == 3:
            detail = '认证失败,请重新认证或联系客服'
        elif verify_state == 4:
            detail = '齐银e已开通,请先试打款'
        elif verify_state == 5:
            detail = '等待试打款'
        if verify_state != 6:
            final_state = 0
        else:
            final_state = 1
            detail = '可以买票'
        # for i in queryset:
        #     print(i.status)
        gj_list = []
        normal_list = []
        if queryset:
            ser_obj = TicketsMallSerializer(queryset, many=True)
            for i in ser_obj.data:
                # print(i)
                if i.get('status') == 'sj' and i.get('fabu_user') == request.user.username:
                    i['status'] = 'gj'
                    # i.pop('piaohao')
                    i.pop('fabu_user')
                    gj_list.append(i)
                else:
                    normal_list.append(i)
            return Response({'ticket': gj_list + normal_list, 'page_total': ticket_count, 'page': page_number,
                             'gongsi_status': [final_state, detail], 'error_code': 1}, status=status.HTTP_200_OK,
                            content_type='application/json')
        # "Access-Control-Allow-Headers":'*'可加可不加,在settings里允许所有的方法了.
        else:
            return Response({'ticket': [], 'error_code': 1},status=status.HTTP_200_OK,)


class Calculate_Ykj2Lilv(APIView):
    '''
    通过一口价来计算利率.
    '''

    def post(self, request):
        logger.info(request._request.body)
        jiaoyi_jiage = request.data.get('jiaoyi_jiage')
        # 十万扣息为空
        ticket_obj = Piaoju.objects.filter(id=request.data.get('id')).first()
        if ticket_obj.status == 'sj':
            real_lilv, real_daozhang = yikoujia2lilv(jiaoyi_jiage, ticket_obj.pm_amount, now().date(),
                                                     ticket_obj.date_daoqi)
            return Response({'error_code': 1, 'jiaoyi_lilv': real_lilv, 'daozhang_money': real_daozhang})
        else:
            return Response({'error_code': 1000, 'detail': '票据已被他人下单,无法改价'})


class ModifyTicketPrice(APIView):
    '''
    票据大厅改价
    '''

    def post(self, request):
        logger.info(request._request.body)
        jiaoyi_jiage = request.data.get('jiaoyi_jiage', '')
        ticket_obj = Piaoju.objects.filter(id=request.data.get('id')).first()
        if jiaoyi_jiage == '':
            return Response({'error_code': 1000, 'detail': '请正确输入'})
        if not ticket_obj:
            return Response({'error_code': 1001, 'detail': '请正确输入'})
        if ticket_obj.status == 'sj':
            real_lilv, real_daozhang = yikoujia2lilv(jiaoyi_jiage, ticket_obj.pm_amount, now().date(),
                                                     ticket_obj.date_daoqi)
            ticket_obj.jiaoyi_jiage = jiaoyi_jiage
            ticket_obj.jiaoyi_lilv = real_lilv
            ticket_obj.daozhang_money = real_daozhang
            ticket_obj.save(update_fields=['jiaoyi_jiage', 'jiaoyi_lilv', 'daozhang_money'])
            return Response({'detail': '改价成功', 'error_code': 1})
        else:
            return Response({'error_code': 1002, 'detail': '票据已被他人下单,无法改价'},
                            content_type="application/json")


class BuyTicketCheck(APIView):
    '''
    点击我要买票详情.
    '''

    # permission_classes = [SuperuserPermission]
    def post(self, request):
        ticket_obj = Piaoju.objects.filter(id=request.data.get('id')).first()
        if not ticket_obj:
            return Response({'error_code': 1002, 'detail': '票据不存在请重新确认'})
        if ticket_obj.status == 'sj':
            try:
                acct_list = BankAccount.objects.filter(gongsi_id=request.user.gongsi_id, acct_type=1)
            except BankAccount.DoesNotExist:
                return Response({'error_code': 1001, 'detail': '签收行不存在,请先添加签收行'})
            else:
                sign_banklist = list(acct_list.values('id', 'bank_name', 'bank_no', 'account'))
                for i in sign_banklist:
                    i['id'] = str(i['id'])
                jindou_total = getTotalJindou(request.user.gongsi)
                jindou_consume = get_order_fee(ticket_obj.piaoju_type, ticket_obj.pm_amount)
                # print(sign_banklist)
                ser_obj = TicketsDetailSerializer(ticket_obj, context=request.user)
                # print(ser_obj.data)
                return Response({'error_code': 1, 'ticket_detail': ser_obj.data, 'qianshou_bank': sign_banklist,
                                 'jindou_total': jindou_total, 'jindou_consume': jindou_consume,
                                 'payment_method': [{'name': '齐银E', 'value': '1'}]})
        else:
            return Response({'error_code': 1000, 'detail': '票据已被他人下单'}, status=status.HTTP_202_ACCEPTED,
                            content_type="application/json")


class TicketImgUpload(APIView):
    '''
    票据上传识别接口
    img_front:正面,img_back:背面,img_duifu:兑付
    '''

    def upload_img(self, img, picname=''.encode('utf8')):
        try:
            ines = img.split('base64,')
        except:
            return Response({'error_code': 1000, 'detail': '请传输base64编码'}, status=status.HTTP_202_ACCEPTED,
                            content_type="application/json")
        imgData = base64.b64decode(ines[1])
        img_name = f"{time.time()}{uuid4()}{time.time()}".encode("utf8")
        img_name = f"{hashlib.md5(img_name + picname).hexdigest()}.jpg"
        img_front_url = os.path.join(settings.MEDIA_ROOT, img_name)
        with open(img_front_url, 'wb') as f:
            f.write(imgData)
        return img_name

    def post(self, request):
        logger.info(request.user.username + ':upload img')
        img_front = request.data.get('img_front', '')  # [1,2,3]
        img_back = request.data.get('img_back', '')
        img_duifu = request.data.get('img_duifu', '')
        context = {}
        if img_front:
            try:
                ines = img_front.split('base64,')
            except:
                return Response({'error_code': 1000, 'detail': '请传输base64编码'}, status=status.HTTP_202_ACCEPTED,
                                content_type="application/json")
            imgData = base64.b64decode(ines[1])
            img_front_name = f"{time.time()}{uuid4()}{time.time()}".encode("utf8")
            img_front_name = f"{hashlib.md5(img_front_name + 'img_front'.encode('utf8')).hexdigest()}.jpg"
            img_front_url = os.path.join(settings.MEDIA_ROOT, img_front_name)
            with open(img_front_url, 'wb') as f:
                f.write(imgData)
            compress_path = image_compress.compress_image(img_front_url)
            # os.remove(img_front_url) 需不需要删除原文件,保留压缩的图片.
            # print(compress_path)
            date_daoqi, piaohao, piaomianjine, chengduiren = baiduocr.img_text(compress_path)
            file_name = compress_path.split('.')[1]
            context['error_code'] = 1
            context['detail'] = '上传成功'
            context['img_url'] = f'http://{settings.IP}/media/{img_front_name}'
            # context['img_url'] = f'http://{settings.IP}/media/{file_name}'
            context['date_daoqi'] = date_daoqi
            context['piaohao'] = piaohao
            context['pm_amount'] = float(piaomianjine) / 10000
            if piaomianjine == 0.0:
                context['pm_amount'] = ''
            context['bank'] = chengduiren
            return Response(context, status=status.HTTP_201_CREATED, content_type='application/json')
        if img_back:
            img_back_name = self.upload_img(img_back, 'img_back'.encode('utf8'))
            context['error_code'] = 1
            context['detail'] = '上传成功'
            context['img_url'] = f'http://{settings.IP}/media/{img_back_name}'
            return Response(context, status=status.HTTP_201_CREATED, content_type="application/json")
        if img_duifu:
            img_duifu_name = self.upload_img(img_duifu, 'img_duifu'.encode('utf8'))
            context['error_code'] = 1
            context['detail'] = '上传成功'
            context['img_url'] = f'http://{settings.IP}/media/{img_duifu_name}'
            return Response(context, status=status.HTTP_201_CREATED, content_type="application/json")

        else:
            return Response({'error_code': 1001, 'detail': '上传失败'}, status=status.HTTP_204_NO_CONTENT,
                            content_type="application/json")


class UpLoadTicket(APIView):
    '''
    银票商票发布API.
    '''

    def post(self, request):
        logger.info(request.data)
        # print(type(request.data))
        num = len(request.data.get('accepter'))
        if request.data.get('piliang', False) == False:
            request.data['piliang'] = [False for i in range(num)]
        # elif request.data.get('piliang',False) == True:
        #     request.data['piliang'] = [True for i in range(num)]
        #     print(request.data['piliang'])
        if request.data.get('dingxiang', False) == False:
            request.data['dingxiang'] = [False for i in range(num)]
        # elif request.data.get('dingxiang',False) == True:
        #     request.data['dingxiang'] = [True for i in range(num)]
        if request.data.get('number', 1) == 1:
            request.data['number'] = [1 for i in range(num)]
        # elif request.data.get('number') != 1:
        #     request.data['number'] = [request.data.get('number') for i in range(num)]
        # 批量添加票据
        for i in range(num):
            piaoju = Piaoju()
            piaoju.piliang = request.data.get("piliang")[i]

            piaoju.dingxiang = request.data.get("piliang")[i]

            piaoju.accepter = request.data.get("accepter")[i]
            # 票据类型自己判断
            if piaoju.accepter == 'yp':
                piaoju.piaoju_type = request.data.get("piaoju_type", "gg")
            if piaoju.accepter == 'sp':
                piaoju.status = 'sh'
                pic1_duifu = request.data.get("img_duifu")[i]
                if pic1_duifu != '':
                    pic1_duifu = pic1_duifu.split('/')[-1]
                piaoju.pic1_duifu = pic1_duifu
            jiaoyi_type = request.data.get("jiaoyi_type")[i]
            jiaoyi_lilv = request.data.get("jiaoyi_lilv")[i]
            piaoju.number_total = request.data.get("number")[i]
            piaoju.piaohao = request.data.get("piaohao")[i]
            piaoju.bank = request.data.get("bank", "")[i]

            # 图片发过来的是路径,取出名字然后进行存储.
            pic1 = request.data.get("img_front")[i]
            if pic1 != '':
                pic1 = pic1.split('/')[-1]
            piaoju.pic1 = pic1
            pic1_back = request.data.get("img_back")[i]
            if pic1_back != '':
                pic1_back = pic1_back.split('/')[-1]
            piaoju.pic1_back = pic1_back
            piaoju.pm_amount = float(request.data.get("pm_amount")[i])
            piaoju.beishucishu = request.data.get("beishu")[i]
            piaoju.flaw_type = request.data.get("flaw_type")[i]
            piaoju.date_daoqi = request.data.get("date_daoqi")[i]
            piaoju.tzdays = request.data.get("tzdays")[i]
            if jiaoyi_type == 'jj':
                piaoju.jiaoyi_lilv = 0
                piaoju.jiaoyi_jiage = 0
                piaoju.jiaoyi_type = jiaoyi_type
            elif jiaoyi_type == 'ykj':
                piaoju.jiaoyi_type = jiaoyi_type
                piaoju.jiaoyi_jiage = request.data.get("jiaoyi_jiage")[i]
                piaoju.jiaoyi_lilv, piaoju.daozhang_money = yikoujia2lilv(piaoju.jiaoyi_jiage, piaoju.pm_amount,
                                                                          now().date(),
                                                                          piaoju.date_daoqi,piaoju.tzdays)
            elif piaoju.jiaoyi_type == 'llj':
                shiwanfee = float(request.data.get("shiwanfee")[i])
                piaoju.jiaoyi_jiage, piaoju.daozhang_money, piaoju.jiaoyi_lilv = lilv2yikoujia(jiaoyi_lilv, shiwanfee,
                                                                                               piaoju.pm_amount,
                                                                                               now().date(),
                                                                                               piaoju.date_daoqi,
                                                                                               piaoju.tzdays)
            piaoju.qiye_category = request.data.get("qiye_category")[i]

            piaoju.qiye_name = request.data.get("qyname", "")[i]
            piaoju.bankaccount_belong_id = request.data.get('bankaccount_belong')[i]
            piaoju.fabu_user = request.user.username
            piaoju.gongsi = request.user.gongsi
            piaoju.save()
        return Response({"error_code": 1, "detail": '发布成功'}, status=status.HTTP_201_CREATED,
                        content_type="application/json")

        # ser_obj = TicketsDetailSerializer(data=request.data,context=request)
        #
        # if ser_obj.is_valid():
        #     # ser_obj.validated_data
        #     ser_obj.save()
        #     return Response({"error_code": 1, "detail": '提交成功'}, status=status.HTTP_201_CREATED)
        # 返回不同的内容
        # return Response({"error_code": 1001, "detail": ser_obj.errors}, status=status.HTTP_202_ACCEPTED)


class BuyTicket(APIView):
    '''
    买票视图
    '''
    def post(self, request):
        context = {}
        logger.info(request._request.body)

        # 取票据信息
        # piaohao = request.data.get("piaohao", "")
        piaoju_id = request.data.get("id", "")
        logger.info(request.user.username + f'买家 下单票据id:{piaoju_id}')
        jingjia = request.data.get("jingjia", False)

        qianshou_bank_id = request.data.get("qianshou_bank")

        piliang = request.data.get("piliang", False)
        piliang_ticket_number = request.data.get('number', '1')

        try:
            piaoju = Piaoju.objects.get(id=piaoju_id)
        except Piaoju.DoesNotExist:
            context["detail"] = "签收行不存在!"
            context["error_code"] = 1003
            return Response(context, content_type="application/json")

        else:
            order = PiaojuOrder()
            print(u'票据剩余张数', piaoju.number_remaining)
            if reach_buyer_processing_order_limit(request.user.username) == True:
                context["detail"] = u"您有多笔订单未完成，请完成当前订单，再进行购票。"
                context["error_code"] = 1002
                return Response(context, content_type="application/json")
            if piliang == True:
                order.number = int(piliang_ticket_number)
                if int(piaoju.number_remaining) < int(piliang_ticket_number):
                    context["detail"] = "票据余量不足!"
                    context["error_code"] = 1000
                    return Response(context, content_type="application/json")

            # 应该是卖家确认接单后
            # if piliang:
            #     number_remaining1 = piaoju.number_remaining - int(piliang_ticket_number)
            #     Piaoju.objects.filter(id=piaoju_id).update(number_remaining=number_remaining1)

            order.buyer = request.user.username
            try:
                qianshou_bank = BankAccount.objects.get(id=qianshou_bank_id)
            except BankAccount.DoesNotExist:
                context["detail"] = "签收行不存在!"
                context["error_code"] = 1002
                return Response(context, content_type="application/json")
            if qianshou_bank.acct_type != 1:
                context["detail"] = "请正确选择签收行!"
                context["error_code"] = 1003
                return Response(context, content_type="application/json")
            order.bankaccount_accept_id = qianshou_bank_id
            order.piaoju = piaoju
            order.seller = piaoju.fabu_user
            order.buyer_gongsi = request.user.gongsi
            order.seller_gongsi = piaoju.gongsi
            order.ordertime = now()
            order.status = 1
            order.lastoptime = now()

            if jingjia == True:
                # order.jj_lilv = request.data.get("jj_lilv", 0)
                # order.jj_shiwanshouxufei = request.data.get("jj_shouxufei", 0)
                order.jj_jiaoyi_jiage = request.data.get("jiaoyi_jiage", 0)
                # models自动给转换格式,字符型转换为浮点型存储.
                print("this is jingjia ----------", order.jj_jiaoyi_jiage)
            order.save()

            msg_type = ''
            if piaoju.accepter == 'sp':
                msg_type = piaoju.get_qiye_category_display()
            elif piaoju.accepter == 'yp' or 'cw':
                msg_type = piaoju.get_piaoju_type_display()
            # 消息提醒,给卖家,买家接单了
            msg = "尊敬的客户您好！您在{}发布的{}-{}万电子承兑票据，买方已接单，请您前往平台完成订单交易。".format(
                piaoju.date_add.strftime("%Y-%m-%d %H:%M:%S").replace('-', '/')[5:], msg_type,
                piaoju.pm_amount
            )
            # msgremind.sendremindmsg(15653373925, msg)
            save_notice("seller", "您有新的订单待处理", piaoju.fabu_user, piaoju.gongsi)
            # TODO  by wzj 保存用户用户通知,然后存储到消息队列里去.然后给用户发信息.
            context["error_code"] = 1

            if jingjia == "true":
                context["detail"] = u"恭喜您,出价成功!"
            else:
                context["detail"] = u"恭喜您,接单成功!"

            # save notice to seller

            return Response(context, content_type="application/json")


class UserOrderView(APIView):
    '''
    买家跟买家的订单视图
    '''
    def post(self, request):
        # logger.info(request._request.body)
        order_time = request.data.get('order_time','today_order')
        current_page = int(request.data.get('current_page',1))
        order_status = request.data.get('order_status', 'all')
        min_date = request.data.get('min_date','')
        max_date = request.data.get('max_date','')
        search_field = request.data.get('search_field','')
        page_num = 10
        context = {}
        print(request._request.path)
        order_menu = copy.deepcopy(ORDER_MENU)
        if request._request.path == '/buyer-order/':
            user_identity = 'buyer'
            query_set = PiaojuOrder.objects.filter(buyer=request.user.username)
        elif request._request.path == '/seller-order/':
            query_set = PiaojuOrder.objects.filter(seller=request.user.username)
            user_identity = 'seller'
        else:
            context['detail'] = '访问路径错误'
            context['error_code'] = 1000
            context['data'] = []
            context['order_count'] = 0
            return Response(context, status=status.HTTP_200_OK,content_type='application/json')
        if order_time == 'today_order':

            query_set = query_set.filter(Q(ordertime__lt=now().date()))
            today_list = []
            if user_identity == 'buyer':
                today_list = query_set.filter(Q(buyer=request.user.username),Q(ordertime__lt=now().date()))
            elif user_identity == 'seller':
                today_list = query_set.filter(Q(seller=request.user.username),Q(ordertime__lt=now().date()))
            today_order_list = list(today_list.values('status'))

            for i in today_order_list:
                if i['status'] == 1 or i['status'] == 2:
                    order_menu['today_order_status'][1]['number'] += 1
                elif i['status'] == 3:
                    order_menu['today_order_status'][2]['number'] += 1
                elif i['status'] == 4:
                    order_menu['today_order_status'][3]['number'] += 1
                elif i['status'] == 5:
                    order_menu['today_order_status'][4]['number'] += 1
                elif i['status'] == 6:
                    order_menu['today_order_status'][5]['number'] += 1
            # order_menu['today_order_status'][1]['number'] = query_set.filter(status__in=[1,2]).count()
            # order_menu['today_order_status'][2]['number'] = query_set.filter(status=3).count()
            # order_menu['today_order_status'][3]['number'] = query_set.filter(status=4).count()
            # order_menu['today_order_status'][4]['number'] = query_set.filter(status=5).count()
            # order_menu['today_order_status'][5]['number'] = query_set.filter(status=6).count()
            if query_set:
                if order_status == 'all':
                    query_set = query_set
                elif order_status == '1-2':
                    query_set = query_set.filter(Q(status=1) | Q(status=2))
                else:
                    query_set = query_set.filter(Q(status=order_status))
            context['menu'] = order_menu

        elif order_time == 'history_order':
            if order_status == 'all':
                query_set = query_set.filter(Q(ordertime__lte=now().date()))
            else:
                query_set = query_set.filter(Q(ordertime__lt=now().date()),Q(status=order_status))
            context['menu'] = ORDER_MENU
        # 筛选日期跟承兑人
        if min_date != '':
            query_set = query_set.filter(ordertime__gte=min_date)
        if max_date != '':
            query_set = query_set.filter(ordertime__lt=max_date)
        if search_field != '':
            if search_field.isdigit:
                query_set = query_set.filter(piaoju__pm_amount=search_field)
            else:
                query_set = query_set.filter(piaoju__bank__icontains=search_field)
        page_start = (current_page - 1) * page_num
        page_end = current_page * page_num
        if query_set:
            order_count = query_set.count()
            query_set = query_set.order_by('-ordertime')[page_start:page_end]
            ser_obj = TicketsOrderSerializer(query_set, many=True)
            context['data'] = ser_obj.data
            context['detail'] = '订单列表'
            context['order_count'] = order_count

            context['error_code'] = 1
            return Response(context, status=status.HTTP_200_OK,content_type='application/json')
        else:
            context['detail'] = '数据为空'
            context['error_code'] = 1001
            context['data'] = []
            context['order_count'] = 0
            context['menu'] = order_menu
            return Response(context, status=status.HTTP_200_OK,content_type='application/json')


class SellerConfirmTicketView(APIView):
    '''
    卖家确认接单视图,所有票据类型.
    '''
    def post(self, request):
        logger.info(request.data)
        orderid = request.data.get("id", 0)

        logger.info(request.user.username + f':卖家确认接单:票据id({orderid})')
        try:
            order = PiaojuOrder.objects.get(id=orderid)
        except PiaojuOrder.DoesNotExist:
            return Response({'error_code':1000,'detail':'票号错误'})
        else:
            if order.status != 1 or order.status != 2:
                return Response({'error_code':1001,'detail':'订单状态错误'}, content_type="application/json")
            if order.status == 1 and order.seller != request.user.username:
                return Response({'error_code': 1002, 'detail': '您不是该票据的发布者'}, content_type="application/json")
            if order.status == 2 and order.buyer != request.user.username:
                return Response({'error_code': 1002, 'detail': '您不是该定向票据的买家'}, content_type="application/json")
            # 改变订单状态为：3 卖方已确认接单
            order.status = 3
            order.lastoptime = now()
            order.ordertime = now()
            '''相关票据状态更新为在交易中'''
            order.piaoju.status = 'indeal'
            order.piaoju.save(update_fields=['status'])
            order.save(update_fields=['status','lastoptime','ordertime'])
            # 将该票据相关的其他进行中的订单做取消处理
            PiaojuOrder.objects.filter(~Q(id=orderid), Q(piaoju_id=order.piaoju.id), ~Q(status=7),
                                            ~Q(status=8)).update(status=8)

            # TODO  by wzj 卖家确认接单,然后存储到消息队列里去.
            if order.piaoju.dingxiang == True:
                msg = f'票号尾号为{order.piaoju.piaohao[-6:]}定向买家已确认接单'
                save_notice("seller", msg, order.seller, order.seller_gongsi_id)
            else:
                msg = f'票号尾号为{order.piaoju.piaohao[-6:]}卖家已确认接单'
                save_notice("buyer", msg, order.buyer, order.buyer_gongsi_id)
            return Response({'error_code': 1, 'detail': '恭喜，订单接单成功'}, content_type="application/json")


class PaymentCheck(APIView):
    '''
    保证金以及票款的支付确认数据通知
    '''
    pass

