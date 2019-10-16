import uuid,time,hashlib
from datetime import datetime, timedelta
from random import choice

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from rest_framework import mixins, permissions, authentication
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler

from users.models import VerifyCode, Opinion
from users.permission import SuperuserPermission
from users.serializers import SmsSerializer, UserDetailSerializer, UserRegSerializer, \
    OpinionModelSerializer,  RepwdSerializer

# 这个方法会去setting中找AUTH_USER_MODEL
# 但是当第三方模块根本不知道你的user model在哪里如何导入呢
# User 就是Userprofile表
User = get_user_model()
# 发送验证码是创建model中一条记录的操作
from rest_framework.mixins import CreateModelMixin
import logging
logging.basicConfig()
logger = logging.getLogger("django")

# Create your views here.


class CustomBackend(ModelBackend):
    """
    自定义用户验证规则
    """

    def authenticate(self, username=None, password=None, **kwargs):
        try:
            # 不希望用户存在两个，get只能有一个。两个是get失败的一种原因
            # 后期可以添加邮箱验证
            user = User.objects.get(
                Q(username=username) | Q(mobile=username))
            # django的后台中密码加密：所以不能password==password
            # UserProfile继承的AbstractUser中有def check_password(self,
            # raw_password):
            if user.check_password(password):
                return user
        except Exception as e:
            return None



class SmsCodeViewset(CreateModelMixin, viewsets.GenericViewSet):
    """
    发送短信验证码
    """
    authentication_classes = []
    serializer_class = SmsSerializer

    def generate_code(self):
        """
        生成四位数字的验证码字符串
        """
        seeds = "1234567890"
        random_str = []
        for i in range(4):
            random_str.append(choice(seeds))

        return "".join(random_str)

    def create(self, request, *args, **kwargs):
        # 获取数据然后传进序列化器进行序列化
        serializer = self.get_serializer(data=request.data)
        # 进行校验
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        # 拿到校验后的结果.
        mobile = serializer.validated_data["mobile"]
        # 生成验证码.
        code = self.generate_code()

        '''
        修改为自己的运营商验证
        # send_sms(code=code, mobile=mobile)
        
        '''
        # TODO  by wzj 验证码用服务商接口发给用户.
        sms_status = {}
        sms_status["code"] = 'success'

        if sms_status["status"] != 'success':
            return Response({
                "mobile": mobile,
                "detail": sms_status["msg"]
            }, status=status.HTTP_202_ACCEPTED)
        else:
            if mobile != request.data.get('mobile',''):
                return Response({
                    "detail": mobile,
                    "error_code": 1000
                },status=status.HTTP_202_ACCEPTED)

            code_record = VerifyCode(code=code, mobile=mobile)
            code_record.save()
            return Response({
                "mobile": mobile,
                "error_code": 1,
            }, status=status.HTTP_201_CREATED)
            # return Response({
            #     serializer.data
            # }, status=status.HTTP_201_CREATED)


# class UserViewset(CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
#     """
#     用户
#     """
#     serializer_class = UserRegSerializer
#     queryset = User.objects.all()
#     authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)
#
#     def get_serializer_class(self):
#         if self.action == "retrieve":
#             return UserDetailSerializer
#         elif self.action == "create":
#             return UserRegSerializer
#
#         return UserDetailSerializer
#
#     # permission_classes = (permissions.IsAuthenticated, )
#     def get_permissions(self):
#         if self.action == "retrieve":
#             return [permissions.IsAuthenticated()]
#         elif self.action == "create":
#             return []
#
#         return []
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = self.perform_create(serializer)
#
#         re_dict = serializer.data
#         payload = jwt_payload_handler(user)
#         re_dict["token"] = jwt_encode_handler(payload)
#         re_dict["name"] = user.name if user.name else user.username
#
#         headers = self.get_success_headers(serializer.data)
#         return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)
#
#     # 重写该方法，不管传什么id，都只返回当前用户
#     def get_object(self):
#         return self.request.user
#
#     def perform_create(self, serializer):
#         return serializer.save()



class TestView(APIView):
    '''
    测试视图
    '''
    # authentication_classes = [] 重写认证列表,为空不执行认证操作,在settings里的全局认证失效.
    # authentication_classes = []

    # authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    permission_classes = [SuperuserPermission]

    # permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({'msg': "认证后才能看到此内容"})


class RegisterView(APIView):
    '''
    注册视图
    '''
    authentication_classes = []

    def post(self, request):
        logger.info(request.data)
        username = request.data.get('username', '')
        password = request.data.get('password', '')
        invitemecode = request.data.get('invitecode')  # 邀请人的邀请码.
        verify_code = request.data.get('captcha', '')  # 验证码.
        is_person = request.data.get('is_person', 0)  # 个人或者企业用户.
        my_invitecode = hex(int(username))

        # if verify_code != '':
        #     verify_obj = VerifyCode.objects.filter(code=verify_code,mobile=username).order_by('id').first()
        #     # 验证码是否存在
        #     if verify_obj:
        #         # 验证码是否过期
        #         if verify_obj.add_time + timedelta(minutes=5) > datetime.now():
        #             user_obj = User.objects.filter(username=username).first()
        #             # 用户名是否存在
        #             if user_obj:
        #                 return Response({"detail": '用户名已存在', "error_code": 1003})
        #             else:
        #                 if username and password:
        #                     # 校验通过 插入数据库
        #                     user_new = User()
        #                     user_new.create_new(username, password, my_invitecode, invitemecode, is_person=is_person)
        #                     return Response({"detail": '注册成功!', "error_code": 1})
        #                 else:
        #                     return Response({"detail": '无效的参数', 'error_code': 1004})
        #         else:
        #             return Response({"detail": '验证码已过期', "error_code": 1002})
        #     else:
        #         return Response({"detail": '无效验证码', "error_code": 1001})
        res = ExamVerifyCode(username, verify_code)
        if res.get('error_code') == 1:
            user_obj = User.objects.filter(username=username)
            # 用户名是否存在
            if user_obj:
                return Response({"detail": '用户名已存在', "error_code": 1003})
            else:
                if username and password:
                    # 校验通过 插入数据库
                    user_new = User()
                    user_new.create_new(username, password, my_invitecode, invitemecode, is_person=is_person)
                    return Response({"detail": '注册成功!', "error_code": 1})
                else:
                    return Response({"detail": '无效的参数', 'error_code': 1004})
        return Response(res, status=status.HTTP_200_OK)


class LoginView(APIView):
    '''
    登陆视图
    '''
    authentication_classes = []

    def post(self, request):
        logger.info(request.data)
        username = request.data.get('username')
        password = request.data.get('password', '')
        is_person = request.data.get('is_person')
        if username and password:
            user_obj = authenticate(username=username,password=password)
            if user_obj:
                # 个人或者企业登陆区分
                if user_obj.is_person != int(is_person):
                    return Response({"detail": "请选择正确登陆方式", "error_code": 1002},status=status.HTTP_202_ACCEPTED)
                # 认证成功
                # 生成token字符串  返回token
                uuid_code = f"{time.time()}{uuid.uuid4()}{time.time()}".encode("utf8")
                token = hashlib.md5(uuid_code + username.encode('utf8')).hexdigest()
                # token = uuid.uuid1().hex
                user_obj.token = token
                user_obj.last_login = datetime.now()
                user_obj.expiration_time = datetime.now() + timedelta(days=7)
                user_obj.save(update_fields=['token', 'expiration_time','last_login'])  # 将token 保存到用户表
                return Response(
                    {"token": token, "error_code": 1, "username": username, "id": user_obj.id, "detail": "登陆成功"})
            else:
                return Response({"detail": "用户名或密码错误", "error_code": 1001},status=status.HTTP_202_ACCEPTED)
        else:
            return Response({"detail": "无效的参数", "error_code": 1000},status=status.HTTP_202_ACCEPTED)


# 分开写增删改查.
# class OpinionListView(ListAPIView, CreateAPIView):
#     queryset = Opinion.objects.all()
#     serializer_class = OpinionSerializer
#
#
# class OpinionDetialView(RetrieveAPIView, DestroyAPIView):
#     queryset = Opinion.objects.all()
#     serializer_class = OpinionSerializer


# class OpinionVieset(ModelViewSet):
#     '''
#     Opinion
#     意见反馈 ModelViewSet快速增删改查,错误返回400.复杂的数据处理就要重写
#     '''
#     authentication_classes = []
#     lookup_field = 'id'
#     queryset = Opinion.objects.all()
#     serializer_class = OpinionModelSerializer


class OpinionListView(APIView):
    """ 使用djangorestful进行json序列化
        Opinion
        意见反馈返回error_code
    """
    authentication_classes = []

    def get(self, request):
        """以json形式返回列表"""
        queryset = Opinion.objects.all()
        # 将数据序列化成json格式
        ser_obj = OpinionModelSerializer(queryset, many=True)
        # 返回
        return Response(ser_obj.data)

    def post(self, request):
        logger.info(request._request.body)
        # 获取提交的数据
        # print(request.data)
        # request 是重新封装的对象 request._request ——》 原来的request对象
        ser_obj = OpinionModelSerializer(data=request.data)
        # 检验通过保存到数据库
        if ser_obj.is_valid():
            # ser_obj.validated_data
            ser_obj.save()
            return Response({"error_code": 1, "detail": '提交成功'}, status=status.HTTP_201_CREATED)
        # 3. 返回不同的内容
        return Response({"error_code": 1001, "detail": ser_obj.errors},status=status.HTTP_202_ACCEPTED)

class ExamVerifyCodeView(APIView):
    '''
    重置密码前的验证码校验
    '''
    authentication_classes = []

    def post(self,request):
        logger.info(request.data)
        # verify_obj = VerifyCode.objects.filter(mobile=request.data.get('username'),code=request.data.get('captcha')).order_by('id').first()
        # if verify_obj:
        #     if verify_obj.used == True:
        #         return Response({"error_code": 2, "detail": '验证码已被使用，请重新获取'}, status=status.HTTP_201_CREATED)
        #     if verify_obj.add_time + timedelta(minutes=5) > datetime.now():
        #         return Response({"error_code": 1, "detail": '验证成功'}, status=status.HTTP_201_CREATED)
        #     else:
        #         return Response({"error_code": 1002, "detail": '验证码已过期!'}, status=status.HTTP_202_ACCEPTED)
        # else:
        #     return Response({"error_code": 1001, "detail": '验证码错误!'}, status=status.HTTP_202_ACCEPTED)
        res = ExamVerifyCode(request.data.get('username'),request.data.get('captcha'))
        return Response(res,status=status.HTTP_200_OK)

class RepasswordView(APIView):
    '''
    重置密码
    '''
    authentication_classes = []

    def post(self,request):
        logger.info(request.data)
        user_obj = User.objects.filter(username=request.data.get('username')).first()
        ser_obj = RepwdSerializer(data=request.data, instance=user_obj, partial=True)
        if ser_obj.is_valid():
            ser_obj.save()
            return Response({"error_code": 1, "detail": '修改密码成功'}, status=status.HTTP_201_CREATED)
        # 验证不通过返回不同的内容
        return Response({"error_code": 1001, "detail": ser_obj.errors}, status=status.HTTP_202_ACCEPTED)


def ExamVerifyCode(mobile,code):
    try:
        verify_obj = VerifyCode.objects.get(mobile=str(mobile),
                                           code=str(code))
    except VerifyCode.DoesNotExist:
        return {"error_code": 1001, "detail": '验证码错误!'}
    else:
        if verify_obj.used == True:
            return {"error_code": 1003, "detail": '验证码已被使用，请重新获取'}
        if verify_obj.add_time + timedelta(minutes=5) > datetime.now():
            verify_obj.used = True
            verify_obj.save(update_fields=['used'])
            return {"error_code": 1, "detail": '验证成功'}
        else:
            return {"error_code": 1002, "detail": '验证码已过期!'}
