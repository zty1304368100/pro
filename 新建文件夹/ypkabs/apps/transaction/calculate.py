# 根据一口价计算利率
import time, datetime,json

from django.http import HttpResponse
import logging

from django.utils.timezone import now

logging.basicConfig()
logger = logging.getLogger("django")



def calculate_yikoujia2lilv(req):
    context = {}
    if req.method == "POST":
        logger.info(req.body)
        shiwankou = req.POST.get("shiwankou", 0)
        piaomian = req.POST.get("piaomian", 0)  # 万元
        date_begin = now().date()
        date_end = req.POST.get("date_end")
        tiaozhengdays = req.POST.get("tiaozhengdays", 0)

        if date_end == '':
            context['errmsg'] = u"请输入票据到期日期!"
            return HttpResponse(json.dumps(context), content_type="application/json")

        stDateEnd = time.strptime(str(date_end), "%Y-%m-%d")
        if datetime.date(stDateEnd.tm_year, stDateEnd.tm_mon, stDateEnd.tm_mday) < now().date():
            context['errmsg'] = u"票据到期日早于今天,请检查!"

        nianlilv, daozhang = yikoujia2lilv(shiwankou, piaomian, date_begin, date_end, tiaozhengdays)
        context["nianlilv"] = round(nianlilv, 2)
        context['daozhang'] = round(daozhang, 5)
    return HttpResponse(json.dumps(context), content_type="application/json")


def yikoujia2lilv(shiwankou, piaomian, date_begin, date_end, tiaozhengdays = 0):
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    print(shiwankou, piaomian, date_begin, date_end,tiaozhengdays)
    #date1 = time.strptime(str(date_begin), "%Y-%m-%d")
    # mod by fls.这里传过来就是date类型了，转为time.struct_time
    date1 = date_begin
    date2 = time.strptime(str(date_end), "%Y-%m-%d")
    # print date1, date2

    total_koufei = (float(piaomian) * 10000 / float(100000)) * float(shiwankou)  # 元
    # print total_koufei
    duration = (datetime.datetime(date2.tm_year, date2.tm_mon, date2.tm_mday) - datetime.datetime(date1.year,
                                                                                                  date1.month,
                                                                                                  date1.day)).days
    if tiaozhengdays:
        duration = int(tiaozhengdays) + duration
    print(duration)
    daozhang = float(piaomian) - float(total_koufei) / float(10000)  # 万元
    print(daozhang)
    nianlilv =  ((float(total_koufei) / 10000) / float(piaomian)) * float(360) / float(duration) * 100
    nianlilv = float('%.2f' % nianlilv)
    return nianlilv,daozhang


# 根据利率+手续费 计算一口价
def calculate_lilv2yikoujia(req):
    context = {}
    if req.method == "POST":
        logger.info(req.body)
        nianlilv = req.POST.get("nianlilv", 0.00)
        shiwanshouxufei = req.POST.get("shiwanshouxufei", 0.00)
        piaomian = req.POST.get("piaomian", 0)  # 万元
        date_begin = now().date()
        date_end = req.POST.get("date_end")
        date_end = req.POST.get("date_end")
        tiaozhengdays = req.POST.get("tiaozhengdays", 0)
        if date_end == '':
            context['errmsg'] = u"请输入票据到期日期!"
            return HttpResponse(json.dumps(context), content_type="application/json")
        stDateEnd = time.strptime(str(date_end), "%Y-%m-%d")
        if datetime.date(stDateEnd.tm_year, stDateEnd.tm_mon, stDateEnd.tm_mday) < now().date():
            context['errmsg'] = u"票据到期日早于今天,请检查!"

        shiwankou, daozhang = lilv2yikoujia(nianlilv, shiwanshouxufei, piaomian, date_begin, date_end,tiaozhengdays)
        context['shiwankouxi'] = round(shiwankou, 2)
        context['daozhang'] = round(daozhang, 5)

    return HttpResponse(json.dumps(context), content_type="application/json")


def lilv2yikoujia(nianlilv, shiwanshouxufei, piaomian, date_begin, date_end,tiaozhengdays = 0):
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    print(nianlilv,shiwanshouxufei, piaomian, date_begin, date_end,tiaozhengdays)
    date1 = time.strptime(str(date_begin), "%Y-%m-%d")
    date2 = time.strptime(str(date_end), "%Y-%m-%d")

    total_shouxufei = (float(piaomian) * 10000 / float(100000)) * float(shiwanshouxufei)  # 元
    print(total_shouxufei)

    duration = (datetime.datetime(date2.tm_year, date2.tm_mon, date2.tm_mday) - datetime.datetime(date1.tm_year,
                                                                                                  date1.tm_mon,
                                                                                                  date1.tm_mday)).days

    duration = int(tiaozhengdays) + duration
    print(duration)

    total_lixi = float(piaomian) * 10000 * float(nianlilv) / float(100) * float(duration) / float(360)  # 元
    real_lilv = (total_lixi + total_shouxufei) / float(piaomian) / float(100000) * float(duration) / float(360)
    real_lilv = float('%.2f' % real_lilv)
    print("total lixi:", total_lixi)

    daozhang = float(piaomian) - float(total_shouxufei + total_lixi) / 10000

    shiwankou = float(total_shouxufei + total_lixi) / float(piaomian) * 10
    return shiwankou,daozhang,real_lilv