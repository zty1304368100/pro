
# 是否使用自己写的认证系统。
from rest_framework.permissions import BasePermission
# from rest_framework.exceptions import PermissionDenied

class SuperuserPermission(BasePermission):
	message = {'error_code':1001,'detail':'没有访问权限'}

	def has_permission(self, request, view):
		# 是否登录 request.user 没有认证成功是一个匿名用户
		if not request.auth:
			return False
		# 对用户的权限进行判断
		if request.user.is_superuser:
			return True
		else:
			return False
			# raise PermissionDenied({''})

