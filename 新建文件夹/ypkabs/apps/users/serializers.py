# encoding: utf-8
from django.contrib.auth.hashers import make_password
# from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
import re
from datetime import datetime, timedelta
from django.conf import settings
from users.models import VerifyCode, Opinion
from rest_framework import serializers
from django.contrib.auth import get_user_model
# from rest_framework.exceptions import AuthenticationFailed

# from rest_framework.exceptions import APIException
User = get_user_model()


class SmsSerializer(serializers.Serializer):
    mobile = serializers.CharField(required=True)
    changepwd = serializers.BooleanField(required=False)
    # add_time = serializers.DateTimeField(required=False,format="%m-%d %H:%M:%S")
    def validate_mobile(self, mobile):
        """
        验证手机号码(函数名称必须为validate_ + 字段名)
        """
        # 手机是否注册

        # if User.objects.filter(mobile=mobile).count():
        #     error_msg = "该手机号已存在"
        #     return error_msg

        # 验证手机号码是否合法
        if not re.match(settings.REGEX_MOBILE, mobile):
            # raise serializers.ValidationError("手机号码非法")
            # raise AuthenticationFailed({
            #         "detail": mobile,
            #         "error_code": 1000
            #     })
            # # return Response({"detail": "手机号码非法"})
            error_msg = "手机号码非法"
            return error_msg

        # 验证码发送频率
        # one_mintes_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        # # 添加时间大于一分钟以前。也就是距离现在还不足一分钟
        # if VerifyCode.objects.filter(add_time__gt=one_mintes_ago, mobile=mobile).count():
        #     # raise serializers.ValidationError("距离上一次发送未超过60s")
        #     error_msg = "距离上一次发送未超过60s"
        #     return error_msg

        return mobile

    def validate(self, attr):
        '''
        print(attr)
        print(attr['mobile'])
        attr: OrderedDict([('mobile', '15653373921'), ('changepwd', True)])
        attr['mobile']:15653373921
        全局钩子要对attr做操作然后返回attr这个OrderedDict的类型数据才可以.
        '''
        # print(attr)
        # print(attr.get('changepwd'))
        # 获取不到修改密码的字段,进行验证是否注册
        if not attr.get('changepwd'):
            if User.objects.filter(username=attr['mobile']).count():
                error_msg = "手机号码已注册"
                # print(attr)
                attr['mobile'] = error_msg
                return attr
        # elif attr.get('changepwd'):
        if attr.get('changepwd'):
            if not User.objects.filter(username=attr['mobile']).count():
                error_msg = "手机号码未注册"
                # print(attr)
                attr['mobile'] = error_msg
                return attr

        return attr


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详情序列化,queryset ----- json
    """

    class Meta:
        model = User
        # fields = ("username", "gender", "birthday", "email", "mobile")
        fields = "__all__"


class UserRegSerializer(serializers.ModelSerializer):
    captcha = serializers.CharField(required=True, write_only=True, max_length=4, min_length=4, label="验证码",
                                    error_messages={
                                        "blank": "请输入验证码",
                                        "required": "请输入验证码",
                                        "max_length": "验证码格式错误",
                                        "min_length": "验证码格式错误"
                                    },
                                    help_text="验证码")
    username = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False,
                                     validators=[UniqueValidator(queryset=User.objects.all(), message="用户已经存在")])

    password = serializers.CharField(
        style={'input_type': 'password'}, help_text="密码", label="密码", write_only=True,
    )

    # 调用父类的create方法，该方法会返回当前model的实例化对象即user。
    # 前面是将父类原有的create进行执行，后面是加入自己的逻辑
    def create(self, validated_data):
        user = super(UserRegSerializer, self).create(validated_data=validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user

    def validate_captcha(self, captcha):

        # get与filter的区别: get有两种异常，一个是有多个，一个是一个都没有。
        # try:
        #     verify_records = VerifyCode.objects.get(mobile=self.initial_data["username"], code=code)
        # except VerifyCode.DoesNotExist as e:
        #     pass
        # except VerifyCode.MultipleObjectsReturned as e:
        #     pass

        # 验证码在数据库中是否存在，用户从前端post过来的值都会放入initial_data里面，排序(最新一条)。
        verify_records = VerifyCode.objects.filter(mobile=self.initial_data["username"]).order_by("-add_time")
        if verify_records:
            # 获取到最新一条
            last_record = verify_records[0]

            # 有效期为五分钟。
            five_mintes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            if five_mintes_ago > last_record.add_time:
                raise serializers.ValidationError("验证码过期")

            if last_record.code != captcha:
                raise serializers.ValidationError("验证码错误")

        else:
            raise serializers.ValidationError("验证码错误")

    # 不加字段名的验证器作用于所有字段之上。attrs是字段 validate之后返回的总的dict
    def validate(self, attrs):
        attrs["mobile"] = attrs["username"]
        del attrs["captcha"]
        return attrs

    class Meta:
        model = User
        fields = ("username", "captcha", "invitecode", "password", 'is_person')


# class OpinionSerializer(serializers.ModelSerializer):

# class Meta:
#     model = Opinion
#     fields = "__all__"

class OpinionModelSerializer(serializers.ModelSerializer):

    # 局部钩子，针对name做校验,attrs就是name字段,全局钩子的attrs是包含所有字段的字典.
    def validate_name(self, attrs):
        print(attrs)
        if '弟弟' in attrs:
            # error_code = 1001
            # return False
            raise serializers.ValidationError('不合法')
        else:
            return attrs


    class Meta:
        model = Opinion
        fields = '__all__'


class RepwdSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=11)
    password = serializers.CharField(required=True)

    # def validate_password(self, attrs):
    #     print('123')
    #     print(make_password(attrs))
    #     return make_password(attrs)

    def update(self, instance, validated_data):
        print(validated_data)
        instance.password = make_password(validated_data.get('password'))
        instance.save()
        return instance

    class Meta:
        model = User
        fields = '__all__'
