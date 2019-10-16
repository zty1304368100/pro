"""eslcampus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf.urls import url
from django.views.static import serve
from rest_framework.documentation import include_docs_urls
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from rest_framework_jwt.views import obtain_jwt_token

# from users.auth import TokenlimitView
from users.auth import TokenlimitView
from users.views import SmsCodeViewset, TestView, LoginView, RegisterView, OpinionListView, \
    RepasswordView, ExamVerifyCodeView

router = DefaultRouter()
# router.register(r'register',UserViewset,base_name='users')
router.register(r'get_captcha', SmsCodeViewset, base_name="get_captcha")
# router.register(r'opinion', OpinionVieset, base_name="opinion")


urlpatterns = [

    path('admin/', admin.site.urls),
    # router的path路径
    re_path(r'^', include(router.urls)),
    # path('ueditor/', include('DjangoUeditor.urls')),
    # path(r'api-auth/', include('rest_framework.urls')),
    # media路径
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    # 与user有关的路径
    url(r'^login/', LoginView.as_view()),
    url(r'^register/', RegisterView.as_view()),
    url(r'^opinion/$', OpinionListView.as_view()),
    url(r'^repwd/$', RepasswordView.as_view()),
    url(r'^bfrepwd/$', ExamVerifyCodeView.as_view()),
    url(r'^tokenlimit/$', TokenlimitView.as_view()),

    # 与业务流程有关路径
    url(r'^', include('transaction.urls')),

    # router注册或者直接url里填写.
    # url(r'^opinion/(?P<id>\d+)/$',
    # OpinionVieset.as_view(actions={'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),

    path(r'test/', TestView.as_view()),
]

# urlpatterns += [
#     # drf 自带的
#     path(r'api-token-auth/', views.obtain_auth_token),
#     # jwt 认证
#     path(r'jwt_login/', obtain_jwt_token),
#  ]
