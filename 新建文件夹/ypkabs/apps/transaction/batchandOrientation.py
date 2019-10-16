import datetime

from django.db.models import Q
from django.utils.timezone import now
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from transaction.calculate import yikoujia2lilv, lilv2yikoujia
from transaction.models import Piaoju, PiaojuOrder
from transaction.serializers import TicketsMallSerializer
from users.auth import DefaultTAuth
import logging

from users.models import UserProfile

logging.basicConfig()
logger = logging.getLogger("django")


class BatchesMallView(APIView):
    '''
    批量买票据大厅视图
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
        if sort_field == 'number':
            sort_field = 'number_remaining'
        # 起始数据
        page_start = (current_page - 1) * page_number
        page_end = current_page * page_number


        # 搜索相关
        search_field = query_dict.get('search_field', '')

        queryset = Piaoju.objects.filter(Q(piliang=True), Q(dingxiang=False), Q(status__in=['sj', 'deal', 'indeal'])
                                         # Q(date_add__gte=now().date()),
                                         )

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


#定向发布票据
class OrientationSell(APIView):
    '''
    定向发布票据api.
    '''

    def post(self, request):
        logger.info(request.data)
        # print(type(request.data))
        num = len(request.data.get('trade_phone'))

        if request.data.get('number', 1) == 1:
            request.data['number'] = [1 for i in range(num)]

        # 批量添加票据
        for i in range(num):
            piaoju = Piaoju()
            trade_phone = request.data.get("trade_phone", "")[i]
            qiye_name = request.data.get("qiye_name", "")[i]
            piaoju.piaohao = request.data.get("piaohao")[i]
            if piaoju.piaohao[0] == '1':
                piaoju.accepter = 'yp'
            elif piaoju.piaohao[0] == '2':
                piaoju.accepter = 'sp'
            try:
                trade_user = UserProfile.objects.get(username=trade_phone)
            except UserProfile.DoesNotExist:
                return Response({'error_code':1000,'detail':'交易对手不存在'})
            if not trade_user.gongsi:
                return Response({'error_code': 1001, 'detail': '交易对手未认证企业'})
            if trade_user.gongsi.name != qiye_name:
                return Response({'error_code': 1002, 'detail': '交易对手企业名称不匹配'})

            piaoju.dingxiang = True

            # 票据类型自己判断
            if piaoju.accepter == 'yp':
                piaoju.piaoju_type = request.data.get("piaoju_type", "gg")
            if piaoju.accepter == 'sp':
                piaoju.status = 'sh'
                pic1_duifu = request.data.get("img_duifu")[i]
                if pic1_duifu != '':
                    pic1_duifu = pic1_duifu.split('/')[-1]
                piaoju.pic1_duifu = pic1_duifu

            piaoju.number_total = request.data.get("number")[i]

            piaoju.bank = request.data.get("bank","")[i]

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
            piaoju.jiaoyi_type = 'ykj'

            piaoju.jiaoyi_jiage = request.data.get("jiaoyi_jiage")[i]
            piaoju.jiaoyi_lilv, piaoju.daozhang_money = yikoujia2lilv(piaoju.jiaoyi_jiage, piaoju.pm_amount,
                                                                      now().date(),
                                                                      piaoju.date_daoqi,piaoju.tzdays)

            piaoju.bankaccount_belong_id = request.data.get('bankaccount_belong')[i]
            piaoju.fabu_user = request.user.username
            piaoju.gongsi = request.user.gongsi
            piaoju.save()
        #   票据存储后生成订单.
            piaoju_order = PiaojuOrder()
            piaoju_order.piaoju_id = piaoju.id
            piaoju_order.buyer_gongsi = trade_user.gongsi
            piaoju_order.buyer = trade_phone
            piaoju_order.seller = request.user.username
            piaoju_order.seller_gongsi = request.user.gongsi
            piaoju_order.ordertime = now()
            piaoju_order.status = 2
            piaoju_order.lastoptime = now()

            piaoju_order.save()
        return Response({"error_code": 1, "detail": '发布成功'}, status=status.HTTP_201_CREATED,
                        content_type="application/json")

