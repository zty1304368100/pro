from django.conf.urls import url
from django.conf import settings
from django.views.generic.base import TemplateView

from transaction.batchandOrientation import BatchesMallView, OrientationSell
from transaction.eventsource import EventSource, MessageInfo
# from transaction.tests import eventsource
from transaction.views import TestView, TicketsMallView, SearchMenuView, UploadMenuView, TicketImgUpload, \
    BuyTicketCheck, Calculate_Ykj2Lilv, ModifyTicketPrice, BuyTicket, UpLoadTicket, OrderMenuView, UserOrderView, \
    SellerConfirmTicketView
from transaction.myviews import TicketsMenu,MyTicket,XJticket,SJticket,Delticket
urlpatterns = [
    url(r'test1/', TestView.as_view()),
    # 菜单视图
    url(r'searchmenu/', SearchMenuView.as_view()),
    url(r'uploadmenu/', UploadMenuView.as_view()),
    url(r'ordermenu/', OrderMenuView.as_view()),
    # 票据大厅
    url(r'ticketsmall/$', TicketsMallView.as_view()),
    url(r'buyticket-check/', BuyTicketCheck.as_view()),
    url(r'modifyticket-price/', ModifyTicketPrice.as_view()),
    url(r'calculate_ykj2lilv/', Calculate_Ykj2Lilv.as_view()),
    url(r'buyticket/$', BuyTicket.as_view()),
    url(r'batchesmall/$', BatchesMallView.as_view()),

    # 票据上传,发布
    url(r'tickets-imgupload/$', TicketImgUpload.as_view()),
    url(r'publish-ticket/$', UpLoadTicket.as_view()),
    url(r'publish-orientationTicket/$', OrientationSell.as_view()),

    url(r'my-tickets/$', MyTicket.as_view()), # 我的票据
    url(r'xj-tickets/$', XJticket.as_view()), # 下架票据
    url(r'sj-tickets/$', SJticket.as_view()), # 上架票据
    url(r'del-tickets/$', Delticket.as_view()), # 删除票据
    url(r'tickets-menu/$', TicketsMenu.as_view()), # 票据菜单

    # 相关推送
    # url(r'test2/$', TemplateView.as_view(template_name="test.html")),
    # url(r'eventsource/$', EventSource.as_view()),
    # url(r'message-info/', MessageInfo.as_view()),

    # 订单接口
    url(r'buyer-order/$', UserOrderView.as_view()),
    url(r'seller-order/$', UserOrderView.as_view()),
    url(r'seller-confirmticket/$', SellerConfirmTicketView.as_view()),

]