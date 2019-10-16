from django.db import models

# Create your models here.

from datetime import datetime,timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
from django.conf import settings
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from rest_framework.authtoken.models import Token
# from demo.models import GongSi, User_person

# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
from transaction.models import User_person, GongSi


class UserProfile(AbstractUser):
    """
    用户信息表,继承AbstractUser。
    增加了字段:token,expiration_time
    修改字段:{personorcompany----is_person}
    """
    mobile = models.CharField(max_length=11, null=True, blank=True, verbose_name="手机号码")
    name = models.CharField(max_length=128, null=False, blank=True, default="", verbose_name=u"姓名")
    address = models.CharField(max_length=100, null=True, blank=True, verbose_name="地址")
    wechat = models.CharField(max_length=256, null=True, blank=True, verbose_name="微信号")
    wechat_img = models.ImageField(upload_to='media', blank=True)
    invitecode = models.CharField(max_length=32, null=False, blank=True, verbose_name="我的邀请码")
    invitemecode = models.CharField(max_length=32, null=False, blank=True, verbose_name="我用的邀请码")
    province = models.IntegerField(default=0, verbose_name="省份")
    city = models.IntegerField(default=0, verbose_name="城市")
    district = models.IntegerField(default=0, verbose_name="区县")
    role = models.IntegerField(default=0, verbose_name="公司角色", choices=((0, u"操作员"), (1, u"经办员"), (2, u"管理员")))
    is_person = models.IntegerField(default=0, verbose_name="公司或个人用户", choices=((0, u"企业用户"), (1, u"个人用户")))
    person = models.OneToOneField(User_person, null=True, blank=True, verbose_name=u"个人认证", related_name="user_person",on_delete=models.CASCADE)
    gongsi = models.ForeignKey(GongSi, null=True, blank=True, verbose_name="所属公司", related_name="user_gongsi",on_delete=models.CASCADE)
    token = models.CharField(max_length=256, null=True, blank=True, verbose_name="token")
    expiration_time = models.DateTimeField(default=datetime.now() + timedelta(days=7), verbose_name="token过期时间")

    # def create_auth_token(sender, instance=None, created=False, **kwargs):
    #     if created:
    #         Token.objects.create(user=instance)

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def create_new(self,acc,passwd,mycode,invitemecode,is_person=0):

        self.username = acc
        self.password = make_password(passwd)
        self.invitecode = mycode
        self.invitemecode = invitemecode
        self.mobile = acc
        self.name = acc
        self.is_person = is_person
        self.save()

    def modify_role(self,acc,role):
        self.role = role
        self.save()

    def __str__(self):
        return self.username

class VerifyCode(models.Model):
    """
    短信验证码,回填验证码进行验证。旧版本引入captcha的app,现自己建表
    """
    code = models.CharField(max_length=10, verbose_name="验证码")
    mobile = models.CharField(max_length=11, verbose_name="电话")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")
    used = models.BooleanField(default=False, verbose_name="是否被使用过")
    # expiration_time = models.DateTimeField(default=datetime.now() + timedelta(minutes=5), verbose_name="验证码过期时间") 不必要

    class Meta:
        verbose_name = "短信验证"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.code


class Opinion(models.Model):
    '''
    意见反馈表,转移到了user的model中,字段名也做了修改.上线前修改旧版意见反馈表一致
    '''
    mobile = models.CharField(max_length=32, verbose_name=u"提交人手机号",null=True,blank=True)
    name = models.CharField(max_length=32, verbose_name=u"提交人姓名",null=True,blank=True)
    content = models.TextField(max_length=1024,verbose_name=u"意见内容",null=True,blank=True)
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"意见提交时间")
    status = models.BooleanField(default=False, verbose_name=u"意见状态")


'''
数据库变化内容
'''