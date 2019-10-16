# encoding: utf-8
import os
from django.conf.urls import url
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
import re
import datetime
import time
from django.conf import settings
from rest_framework import serializers, status
from django.contrib.auth import get_user_model
# from rest_framework.exceptions import AuthenticationFailed
# from rest_framework.exceptions import APIException
from transaction import models

User = get_user_model()


class TicketsMallSerializer(serializers.ModelSerializer):
    # jiaoyi_type = serializers.CharField(source='get_jiaoyi_type_display')
    date_add = serializers.SerializerMethodField()
    remain_days = serializers.SerializerMethodField()
    number = serializers.IntegerField(source='number_remaining')

    # status = serializers.SerializerMethodField()

    # accepter = serializers.CharField(source='get_accepter_display')

    def get_date_add(self, obj):

        return (int(round(time.mktime(obj.date_add.timetuple()) * 1000)))  # 返回出票日期的时间戳

    def get_remain_days(self, obj):
        date1 = now().date()
        date2 = time.strptime(str(obj.date_daoqi), "%Y-%m-%d")

        duration = (datetime.datetime(date2.tm_year, date2.tm_mon, date2.tm_mday) - datetime.datetime(date1.year,
                                                                                                      date1.month,
                                                                                                      date1.day)).days
        remain_time = duration

        return remain_time

    # def get_status(self, obj):
    #     if obj.status == 'indeal':
    #         return '正在交易'
    #     elif obj.status == 'sj':
    #         return '我要买票'

    class Meta:
        model = models.Piaoju
        # 需要判断是否改价,所以需要fabu_user字段
        fields = ['id', 'date_add', 'bank', 'pm_amount', 'date_daoqi', 'remain_days', 'jiaoyi_jiage', 'flaw_type',
                  'jiaoyi_lilv', 'jiaoyi_type', "status", 'accepter', 'fabu_user', 'tzdays', 'number']
        # exclude = ['id','dingxiang','piliang']
        # depth = 2
        extra_kwargs = {
            'piaoju_type': {'source': 'get_piaoju_type_display'},
            'jiaoyi_type': {'source': 'get_jiaoyi_type_display'},
            'flaw_type': {'source': 'get_flaw_type_display'},
            # 'date_daoqi': {'format':'get_piaoju_type_display'}
        }


# print(socket.gethostbyname(socket.getfqdn(socket.gethostname())))


class TicketsDetailSerializer(serializers.ModelSerializer):
    date_add = serializers.SerializerMethodField()
    remain_days = serializers.SerializerMethodField()
    pic = serializers.SerializerMethodField()

    def get_pic(self, obj):
        # pic1 = os.path.join(settings.MEDIA_ROOT,str(obj.pic1))
        pic1 = f'http://{settings.IP}/media/{str(obj.pic1)}'
        if obj.accepter == 'sp':
            # pic_duifu = os.path.join(settings.MEDIA_ROOT,str(obj.pic1_duifu))
            pic_duifu = f'http://{settings.IP}/media/{str(obj.pic1_duifu)}'
            return [pic1, pic_duifu]
        else:
            return [pic1]

    def get_date_add(self, obj):
        # print(self.context.username,'123')
        return (int(round(time.mktime(obj.date_add.timetuple()) * 1000)))  # 返回出票日期的时间戳

    def get_remain_days(self, obj):
        date1 = now().date()
        date2 = time.strptime(str(obj.date_daoqi), "%Y-%m-%d")

        duration = (datetime.datetime(date2.tm_year, date2.tm_mon, date2.tm_mday) - datetime.datetime(date1.year,
                                                                                                      date1.month,
                                                                                                      date1.day)).days
        remain_time = duration  # type:int

        return '(剩' + str(remain_time) + '天)'

    class Meta:
        model = models.Piaoju
        fields = ['id', 'date_add', 'bank', 'pm_amount', 'date_daoqi', 'remain_days', 'jiaoyi_jiage', 'flaw_type',
                  'jiaoyi_lilv', 'jiaoyi_type', "status", 'accepter', 'piaohao', 'pic', 'beishucishu','piliang']

        extra_kwargs = {
            'piaoju_type': {'source': 'get_piaoju_type_display'},
            'jiaoyi_type': {'source': 'get_jiaoyi_type_display'},
            'flaw_type': {'source': 'get_flaw_type_display'},
        }


class TicketsUploadSerializer(serializers.ModelSerializer):
    fabu_user = serializers.SerializerMethodField()

    def get_fabu_user(self):
        return self.context.username

    def validate(self, attr):
        if attr.pic1 != '':
            attr.pic1 = attr.pic1.split('/')[-1]
        if attr.pic1_back != '':
            attr.pic1_back = attr.pic1_back.split('/')[-1]
        if attr.pic1_duifu != '':
            attr.pic1_duifu = attr.pic1_duifu.split('/')[-1]
        return attr

    class Meta:

        model = models.Piaoju
        fields = '__all__'


class TicketsOrderSerializer(serializers.ModelSerializer):
    # fabu_user = serializers.SerializerMethodField()
    piaohao = serializers.SerializerMethodField()
    ordertime = serializers.SerializerMethodField()
    # jiaoyi_jiage = serializers.SerializerMethodField()
    date_daoqi = serializers.SerializerMethodField()
    bank = serializers.SerializerMethodField()
    pm_amount = serializers.CharField(source='piaoju.pm_amount')
    jiaoyi_jiage = serializers.CharField(source='piaoju.jiaoyi_jiage')
    jiaoyi_lilv = serializers.CharField(source='piaoju.jiaoyi_lilv')

    # def get_fabu_user(self):
    #     return self.context.username
    def get_ordertime(self, obj):
        # print(self.context.username,'123')
        return (int(round(time.mktime(obj.ordertime.timetuple()) * 1000)))  # 返回出票日期的时间戳

    def get_piaohao(self, obj):
        return obj.piaoju.piaohao[-6:]

    def get_bank(self, obj):
        return obj.piaoju.bank

    # def get_jiaoyi_jiage(self,obj):
    #     return obj.piaoju.jiaoyi_jiage
    def get_date_daoqi(self, obj):
        return obj.piaoju.date_daoqi

    def validate(self, attr):
        if attr.pic1 != '':
            attr.pic1 = attr.pic1.split('/')[-1]
        if attr.pic1_back != '':
            attr.pic1_back = attr.pic1_back.split('/')[-1]
        if attr.pic1_duifu != '':
            attr.pic1_duifu = attr.pic1_duifu.split('/')[-1]
        return attr

    class Meta:

        model = models.PiaojuOrder
        fields = ['id', 'ordertime', 'bank', 'date_daoqi', 'pm_amount', 'piaohao', 'jiaoyi_jiage', 'status',
                  'jiaoyi_lilv','status_hanzi']

        extra_kwargs = {
            'status_hanzi': {'source': 'get_status_display'},
        }







class MyTicketSerializer(serializers.ModelSerializer):
    # jiaoyi_type = serializers.CharField(source='get_jiaoyi_type_display')
    date_add = serializers.SerializerMethodField()
    remain_days = serializers.SerializerMethodField()
    number = serializers.IntegerField(source='number_remaining')


    # status = serializers.SerializerMethodField()

    # accepter = serializers.CharField(source='get_accepter_display')

    def get_date_add(self, obj):

        return (int(round(time.mktime(obj.date_add.timetuple()) * 1000)))  # 返回出票日期的时间戳

    def get_remain_days(self, obj):
        date1 = now().date()
        date2 = time.strptime(str(obj.date_daoqi), "%Y-%m-%d")

        duration = (datetime.datetime(date2.tm_year, date2.tm_mon, date2.tm_mday) - datetime.datetime(date1.year,
                                                                                                      date1.month,
                                                                                                      date1.day)).days
        remain_time = duration

        return remain_time

    # def get_status(self, obj):
    #     if obj.status == 'indeal':
    #         return '正在交易'
    #     elif obj.status == 'sj':
    #         return '我要买票'

    class Meta:
        model = models.Piaoju
        # 需要判断是否改价,所以需要fabu_user字段
        fields = ['id', 'date_add', 'bank', 'pm_amount', 'date_daoqi', 'remain_days', 'jiaoyi_jiage', 'flaw_type',
                  'jiaoyi_lilv', 'jiaoyi_type', "status", 'accepter', 'fabu_user', 'tzdays', 'number','status_han']
        # exclude = ['id','dingxiang','piliang']
        # depth = 2
        extra_kwargs = {
            'piaoju_type': {'source': 'get_piaoju_type_display'},
            'jiaoyi_type': {'source': 'get_jiaoyi_type_display'},
            'flaw_type': {'source': 'get_flaw_type_display'},
            'status_han': {'source': 'get_status_display'},
            # 'date_daoqi': {'format':'get_piaoju_type_display'}
        }