from datetime import datetime

from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response


from users.models import UserProfile

class DefaultTAuth(BaseAuthentication):

    def authenticate(self, request):
        # 获取用户的token
        # body里的token
        # token = request.data.get('token')
        # header里的token
        token = request._request.META.get('HTTP_TOKEN','')
        if request.query_params.get('token','') != '' and token == '':
            token = request.query_params.get('token','')
        # print(token)
        if not token:
            raise AuthenticationFailed({'detail': '参数无效', 'error_code': 1001})
        # 查询用户表中是否有相应的token
        try:
            user_obj = UserProfile.objects.get(token=token)
        except UserProfile.DoesNotExist:
            # 根据token查询user不存在就认证失败
            raise AuthenticationFailed({'detail': '认证失败', 'error_code': 1002})
        else:
            if user_obj.expiration_time > datetime.now():
                # print(user_obj)
                return user_obj, token
            # 	request.user	request.auth
            else:
                raise AuthenticationFailed({'detail': '认证过期', 'error_code': 1003})




from rest_framework.views import APIView

class TokenlimitView(APIView):

    def post(self,request):
        token = request._request.META.get('HTTP_TOKEN','')
        if request.query_params.get('token','') != '' and token == '':
            token = request.query_params.get('token','')
        if not token:
            return Response({'detail': '参数无效', 'error_code': 1001})
        try:
            user_obj = UserProfile.objects.get(token=token)

        except UserProfile.DoesNotExist:
            raise AuthenticationFailed({'detail': '认证失败', 'error_code': 1002})
        else:
            # 认证过期.
            if user_obj.expiration_time > datetime.now():
                return Response({'detail': '认证通过', 'error_code': 1})
            # 	request.user	request.auth
            else:
                return Response({'detail': '认证过期', 'error_code': 1003})

from rest_framework.views import exception_handler
# 自定义异常返回状态
def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response.data:
        return Response(response.data,status=status.HTTP_202_ACCEPTED)
    else:
        return Response({"error_code":0,"detail":'服务器内部错误!'},status=status.HTTP_202_ACCEPTED)
