from django.db.models import Q
from django.utils.timezone import now

from transaction.models import Notice, Jindou, PiaojuOrder


def save_notice(msgtype, msg, user, gongsi):
    notice = Notice()
    notice.msgtime = now()
    notice.msgtype = msgtype
    notice.msg = msg
    notice.user = user
    notice.gongsi = gongsi
    notice.status = "unread"
    notice.save()
    return True


def getTotalJindou(gs):
    try:
        obj = Jindou.objects.get(gongsi=gs)
    except Jindou.DoesNotExist:
        return 0
    else:
        return obj.total

def get_order_fee(piaoju_type, piaomianjine):
    fee = 0
    if piaoju_type == "sp":
        fee = 10
        if piaomianjine >= 5:
            fee = round(piaomianjine * 10)  # 千分之一
    elif piaoju_type == "cw":
        fee = 10
        if piaomianjine > 10:
            fee = round(piaomianjine * 1)  # 万分之一
            if fee > 300:
                fee = 300
        elif piaomianjine <=1:
                fee = 1
    else:
        fee = 0  # 其他类型不收费
    return fee

# 限制用户购买数量
def reach_buyer_processing_order_limit(pbuyer):
    # 取用户进行中的订单数量
    orders = PiaojuOrder.objects.filter(Q(buyer=pbuyer), ~Q(status=7), ~Q(status=8))
    # 上限5个
    if len(orders) >= 100:
        return True
    else:
        return False