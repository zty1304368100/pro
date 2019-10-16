from datetime import datetime

from django.db import models

# Create your models here.
from django.utils import timezone


class GongSi(models.Model):
    '''
    公司表,未修改字段
    '''
    name = models.CharField(max_length=140, verbose_name="公司名", db_index=True)
    licenceid = models.CharField(max_length=20, null=False, blank=True, verbose_name="统一社会信用代码", unique=True)
    validperiod = models.DateTimeField(default=datetime.now, verbose_name="营业期限")
    capital = models.CharField(max_length=100, default="0", verbose_name="注册资本")
    faren = models.CharField(max_length=128, verbose_name="法人代表")
    faren_id = models.CharField(max_length=20, null=False, blank=True, default="0", verbose_name="法人身份证号")
    faren_tel = models.CharField(max_length=11, null=False, blank=True, default="00000000000", verbose_name="法人电话")
    shikong = models.CharField(max_length=128, verbose_name="实控人", default="")
    shikong_id = models.CharField(max_length=20, null=False, blank=True, default="", verbose_name="实控人身份证号")
    shikong_tel = models.CharField(max_length=11, null=False, blank=True, default="", verbose_name="实控人电话")
    caiwu = models.CharField(max_length=128, default="", verbose_name="财务人员")
    caiwu_id = models.CharField(max_length=20, null=False, blank=True, default="0", verbose_name="财务人员身份证号")
    caiwu_mobile = models.CharField(max_length=11, null=False, blank=True, default="00000000000",
                                    verbose_name="财务人员电话")
    verify_state = models.IntegerField(
        choices=((0, "未认证"), (1, "审核中"), (2, "认证通过"), (3, "认证失败"), (4, "齐银e已开通"), (5, "等待试打款"), (6, "资金账户已绑定")),
        verbose_name="认证状态")
    kaihuzhanghao = models.CharField(max_length=128, null=False, blank=True, verbose_name="开户帐号")
    kaihuhang = models.CharField(max_length=128, verbose_name="开户行", null=False, blank=True)
    kaihuhanghao = models.CharField(max_length=128, verbose_name="开户行号", null=False, blank=True)
    area = models.CharField(max_length=100, null=False, blank=True, verbose_name="所在地")
    contact_tel = models.CharField(max_length=11, null=False, blank=True, verbose_name="联系电话")
    contact_email = models.CharField(max_length=128, null=False, blank=True, verbose_name="联系人邮箱")
    my_invite_code = models.CharField(max_length=6, null=False, blank=True, verbose_name="我的邀请码")
    invited_code = models.CharField(max_length=6, null=False, blank=True, verbose_name="被邀请使用的邀请码")
    invited_qiye = models.CharField(max_length=6, null=False, blank=True, verbose_name="我的邀请人(公司)")
    star_level = models.IntegerField(default=1, verbose_name="帐号星级")
    commiter = models.CharField(max_length=11, null=True, blank=True, verbose_name="认证信息提交者")
    pic_licence = models.ImageField(upload_to="resource/qiye", verbose_name="营业执照", blank=True)
    pic_faren = models.ImageField(upload_to="resource/qiye", verbose_name="法人身份证正面", blank=True)
    pic_faren_back = models.ImageField(upload_to="resource/qiye", verbose_name="法人身份证背面", blank=True)
    pic_shikong = models.ImageField(upload_to="resource/qiye", verbose_name="实控人身份证正面", blank=True)
    pic_shikong_back = models.ImageField(upload_to="resource/qiye", verbose_name="实控人身份证背面", blank=True)
    pic_weituoshu = models.ImageField(upload_to="resource/qiye", verbose_name="委托书", blank=True)
    addtime = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "公司信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def can_pub_piaoju(self):
        if self.verify_state == 3 or self.verify_state == 5 or self.verify_state == 6 or self.verify_state == 7:
            return True
        else:
            return False


class Piaoju(models.Model):
    '''
    票据表修改字段 {xiaci----flaw_type,piaomianjine---pm_amount}
    票据表新增字段 {accepter:承兑人类型,tzdays:调整天数}
    票据表删除字段 {shiwankouxi,qiye_type}
    '''
    # name = models.CharField(max_length=128, verbose_name="票据名称") # 名称没有必要

    accepter = models.CharField(choices=(
        ("cw", "财务"), ("sp", "商票"), ("yp", "银票")),
        max_length=4, verbose_name="承兑人类型")
    # fabu_gongsi	= models.CharField(max_length=128, verbose_name="发布企业")
    gongsi = models.ForeignKey(GongSi, related_name="piaoju_gongsi", verbose_name="票据发布公司", default="",
                               on_delete=models.CASCADE)
    fabu_user = models.CharField(max_length=128, verbose_name="发布人")
    bank = models.CharField(max_length=128, verbose_name="承兑行")
    piaohao = models.CharField(max_length=50, verbose_name="票号")
    piaoju_type = models.CharField(choices=(
        ("gg", "国股"), ("cs", "城商"), ("sn", "三农"), ("cz", "村镇"), ("other", "其它")), blank=True,
        max_length=4, verbose_name="票据类型")
    date_chupiao = models.DateTimeField(default=datetime.now, verbose_name="出票日期")
    date_daoqi = models.DateField(default=datetime.now().date(), verbose_name="到期日期")
    # date_add = models.CharField(max_length=32, default=datetime.now, verbose_name="添加日期")
    date_add = models.DateTimeField(default=datetime.now, verbose_name="添加日期")
    pm_amount = models.FloatField(default=0, null=False, verbose_name="票面金额(万元)")
    # jiaoyi_jiage = models.FloatField(default=0, verbose_name="价格")
    # shiwankoufei = models.FloatField(default=0, null=False, verbose_name="每十万扣费")
    jiaoyi_jiage = models.FloatField(default=0, verbose_name="每十万扣息")
    jiaoyi_type = models.CharField(choices=(("jj", "竞价"), ("ykj", "一口价"), ("llj", "利率价")), max_length=4,
                                   verbose_name="交易类型")
    jiaoyi_lilv = models.FloatField(default=0, null=False, verbose_name="年化利率")
    status = models.CharField(
        choices=(("sh", "审核中"), ("sj", "上架售卖"), ('gj', '改价'), ("xj", "已下架"), ('indeal', '正在交易'), ("deal", "交易完成"),
                 ('reject', '审核不通过')), default="sj",
        max_length=7, verbose_name="票据状态")
    history_status = models.CharField(choices=(("rsj", "重新上架"),("deal", "交易完成")),
                                      max_length=7, verbose_name="票据状态")
    number_total = models.IntegerField(default=1, verbose_name="总张数")
    number_sold = models.IntegerField(default=0, verbose_name="已出张数")
    number_remaining = models.IntegerField(default=1, verbose_name="剩余张数")
    pic1 = models.ImageField(upload_to='media', blank=True, verbose_name="票据正面")
    pic1_back = models.ImageField(upload_to='media', blank=True, verbose_name="票据背面")
    pic1_duifu = models.ImageField(upload_to='media', blank=True, verbose_name="兑付信息")
    beishucishu = models.IntegerField(default=1, verbose_name="背书手数")
    piliang = models.BooleanField(default=False, verbose_name="是否批量")
    dingxiang = models.BooleanField(default=False, verbose_name="是否定向")
    flaw_type = models.CharField(
        choices=(("no", "无瑕疵"), ("cf", "重复背书"), ("ht", "回头"), ("byz", "上下不一致"), ("other", "其他")), max_length=10,
        default="no", verbose_name="瑕疵类型")
    # qiye_type = models.CharField(choices=(("ss", "上市"), ("yq", "央企"), ("gq", "国企"), ("other", "其它")), max_length=6, verbose_name="商票企业类型", default="other")
    # qiye_name = models.CharField(choices=(("hd", "恒大"), ("jk", "金科"), ("rc", "融创"),("rs","荣盛"),("bgy","碧桂园"),("lh","龙湖"),("ld","绿地"),("hxxf","华夏幸福"), ("other", "其它")), max_length=6, verbose_name="商票企业类型", default="other")
    # 商票详细类型。
    # qiye_type = models.CharField(choices=(("ss", "上市"), ("yq", "央企"), ("gq", "国企"), ("other", "其它")), max_length=6,
    #                              verbose_name="商票企业类型", default="other")
    qiye_category = models.CharField(
        choices=(("dc", "地产"), ("jx", "机械制造"), ("hg", "化工"), ("jg", "建工"), ("ht", "航天军工"), ("other", "其它")),
        max_length=6, verbose_name="行业类别", default="other")
    qiye_name = models.CharField(choices=(
        ("hd", "恒大"), ("jk", "金科"), ("rc", "融创"), ("rs", "荣盛"), ("bgy", "碧桂园"), ("lh", "龙湖"), ("ld", "绿地"),
        ("hxxf", "华夏幸福"), ("other", "其它")), max_length=6, verbose_name="地产行业细分", default="other")
    daozhang_money = models.FloatField(default=0, null=False, verbose_name="到账金额")
    bankaccount_belong = models.ForeignKey('BankAccount', related_name="piaoju_bank", null=True,
                                           verbose_name="卖方票据所在户", on_delete=models.CASCADE)
    tzdays = models.IntegerField(default=0, verbose_name="调整天数")

    class Meta:
        verbose_name = "票据"
        verbose_name_plural = verbose_name

    def can_shangjia(self):
        if self.status == "xj" and self.date_daoqi > datetime.now().date():
            return True
        else:
            return False

    def remain_days(self):
        if self.date_daoqi >= datetime.now().date():
            return (self.date_daoqi - datetime.now().date()).days
        else:
            return 0

    def __setitem__(self, k, v):
        self.k = v

    # def __str__(self):
    #     return self.name


# 订单表
class PiaojuOrder(models.Model):
    '''
    订单表 表名{demo_PiaojuOrder-----PiaojuOrder}
    删除字段:{jj_lilv,jj_shiwanshouxufei})
    更改名称字段:{jj_shiwankouxi---jj_jiaoyijiage}
    '''
    piaoju = models.ForeignKey(Piaoju, related_name="order_piaoju", verbose_name="票据", on_delete=models.CASCADE)
    number = models.IntegerField(default=1, verbose_name="订单张数")
    ordertime = models.DateTimeField(default=datetime.now, verbose_name="订单生成时间")
    lastoptime = models.DateTimeField(default=datetime.now, verbose_name="最近一次操作的时间")
    buyer = models.CharField(max_length=128, default="", verbose_name="买方用户id")
    seller = models.CharField(max_length=128, default="", verbose_name="卖方用户id")
    buyer_gongsi = models.ForeignKey(GongSi, related_name="order_gongsi_buyer", verbose_name="买方公司", default="",
                                     on_delete=models.CASCADE)
    seller_gongsi = models.ForeignKey(GongSi, related_name="order_gongsi_seller", verbose_name="卖方公司", default="",
                                      on_delete=models.CASCADE)
    status = models.IntegerField(choices=(
        (0, "无"), (1, "买方已下单"), (2, '定向买方确认接单'), (3, "卖方已确认"), (4, "已付保证金"), (5, "买方已打款"), (6, "卖方已背书"), (7, "交易完成"),
        (8, "订单取消"),), default=0, verbose_name="交易状态")
    baozhengjin_status = models.IntegerField(
        choices=((0, u'双方未付'), (1, u'买家已付'), (2, u'卖家已付'), (3, u'双方已付'), (4, "保证金已退"), (5, "保证金已扣除")), default=0,
        verbose_name="保证金状态")
    baozhengjin = models.FloatField(default=0.0, verbose_name="保证金金额")
    yixiangjin = models.IntegerField(default=500, verbose_name="意向金")
    fee_buyer = models.IntegerField(default=0, verbose_name="买方手续费")
    fee_seller = models.IntegerField(default=0, verbose_name="卖方手续费")
    fukuan_orderno = models.CharField(max_length=32, default="", verbose_name="订单预付款银行orderno")
    # fukuan_orderdate格式:yyyyMMdd
    fukuan_orderdate = models.CharField(max_length=8, default="", verbose_name="订单预付款银行orderdate")
    cancelreason = models.CharField(max_length=128, default="", verbose_name="订单取消原因")
    # jj_lilv = models.FloatField(default=0, verbose_name="竞价-年利率")
    # jj_shiwanshouxufei = models.IntegerField(default=0, verbose_name="竞价-十万手续费")
    jj_jiaoyi_jiage = models.FloatField(default=0, verbose_name="竞价-十万扣息")
    bankaccount_accept = models.ForeignKey('BankAccount', related_name="order_bank", null=True, blank=True,
                                           verbose_name="买方签收行", on_delete=models.CASCADE)
    auto_urged = models.IntegerField(default=0, verbose_name="是否已经自动催办")

    class Meta:
        verbose_name = "票据交易"
        verbose_name_plural = verbose_name


# 个人用户表
class User_person(models.Model):
    name = models.CharField(max_length=140, verbose_name="姓名", db_index=True)
    person_idcard = models.CharField(max_length=20, null=False, blank=True, default="0", verbose_name="个人用户身份证号")
    verify_state = models.IntegerField(
        choices=((0, "未认证"), (1, "审核中"), (3, "认证通过"), (4, "认证失败"), (5, "齐银e已开通"), (6, "资金账户已绑定")),
        verbose_name="认证状态")
    bankaccount = models.CharField(max_length=128, verbose_name="提现账户", null=False, blank=True)
    contact_tel = models.CharField(max_length=11, null=False, blank=True, verbose_name="联系电话")
    star_level = models.IntegerField(choices=((20, "提成20%"), (30, "提成30%"), (40, "提成40%"), (50, "提成50%")),
                                     default=20, verbose_name="帐号星级")
    addtime = models.DateTimeField(default=datetime.now, verbose_name="添加时间")
    pic_person = models.ImageField(upload_to="resource/person", verbose_name="个人身份证正面", blank=True)
    pic_person_back = models.ImageField(upload_to="resource/person", verbose_name="个人身份证背面", blank=True)
    pic_bankcard = models.ImageField(upload_to="resource/person", verbose_name="个人银行卡", blank=True)
    kaihu_bankname = models.CharField(max_length=128, verbose_name="提现账户开户行", null=False, blank=True)

    # my_invite_code = models.CharField(max_length=6, null=False, blank=True, verbose_name="我的邀请码")
    # invited_qiye = models.CharField(max_length=6, null=False, blank=True, verbose_name="我的邀请人(公司)")
    class Meta:
        verbose_name = "个人用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 银行账户相关
class BankAccount(models.Model):
    '''
    银行账户相关
    '''
    gongsi = models.ForeignKey(GongSi, related_name="gongsi_bank_acct", verbose_name="公司", on_delete=models.CASCADE)
    acct_type = models.IntegerField(choices=((0, "电票所在户"), (1, "签收户"), (2, "充值户"), (3, "提现户")), default=0,
                                    verbose_name="账户类型")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添时间")
    bank_name = models.CharField(max_length=144, default="", verbose_name="开户行名称")
    bank_no = models.CharField(max_length=144, default="", verbose_name="开户行号")
    account = models.CharField(max_length=144, default="", verbose_name="银行账号", db_index=True)
    operator = models.CharField(max_length=128, default="", verbose_name="操作者")

    class Meta:
        verbose_name = "企业银行账户表"
        verbose_name_plural = verbose_name


# 商票黑名单
class Black_bussinesscompany_list(models.Model):
    company_name = models.CharField(max_length=128, verbose_name="黑名单公司名")

    class Meta:
        verbose_name = "商票黑名单"
        verbose_name_plural = verbose_name


# 平台帐号记录表
# 生成和记录平台保证金虚户、平台金豆收款虚户
class PingTaiAcctInfo(models.Model):
    gongsi_id = models.IntegerField(default=0, verbose_name="平台账户的公司id")
    gongsi_name = models.CharField(max_length=140, default="", verbose_name="平台账户的公司名")
    gongsi_licenceid = models.CharField(max_length=20, null=False, blank=True, verbose_name="统一社会信用代码")
    gongsi_legal = models.CharField(max_length=128, default="", verbose_name="法人代表")
    gongsi_legal_id = models.CharField(max_length=20, null=False, blank=True, default="0", verbose_name="法人身份证号")
    gongsi_agent = models.CharField(max_length=128, default="", verbose_name="经办人")
    gongsi_agent_id = models.CharField(max_length=20, null=False, blank=True, default="", verbose_name="经办人身份证号")
    contact_tel = models.CharField(max_length=11, null=False, blank=True, default="", verbose_name="联系电话")
    usage_type = models.IntegerField(choices=((0, "无"), (1, "保证金虚户"), (2, "金豆充值虚户")), default=0,
                                     verbose_name="帐号用途")
    acct_type = models.CharField(max_length=2, default="01",
                                 choices=(("01", "普通账户"), ("02", "回款账户"), ("03", "普通附加账户")), verbose_name="资金账户类型")
    SubAcctNo = models.CharField(max_length=32, default="", verbose_name="公司资金账户(齐银e)")
    SubAcctName = models.CharField(max_length=140, default="", verbose_name="公司资金户名(齐银e)")
    BankNo = models.CharField(max_length=12, default="", verbose_name="账户开户行号")
    BankName = models.CharField(max_length=255, default="", verbose_name="账户开户行名")
    BindAcctNo = models.CharField(max_length=32, default="", verbose_name="绑定账户帐号")
    BindBankNo = models.CharField(max_length=12, default="", verbose_name="绑定账户开户行号")
    BindBankName = models.CharField(max_length=255, default="", verbose_name="绑定账户开户行名")
    BindStatus = models.IntegerField(default=0, verbose_name="帐户绑定状态")

    class Meta:
        verbose_name = "公司资金账户"
        verbose_name_plural = verbose_name


# 申诉相关
class Order_appeal(models.Model):
    '''
    订单仲裁,未修改内容
    '''
    order = models.OneToOneField(PiaojuOrder, related_name="order_appeal", verbose_name="订单", db_index=True,
                                 on_delete=models.CASCADE)
    appeal_status = models.BooleanField(default=False, verbose_name="是否处于申诉仲裁状态")
    applyer = models.CharField(max_length=32, null=True, blank=True, verbose_name="申诉人")
    applyer_identify = models.IntegerField(default=0, choices=((0, '买家'), (1, '卖家')))
    apply_reason = models.CharField(max_length=32, null=True, blank=True, verbose_name="申诉理由")
    apply_reason_text = models.CharField(max_length=256, null=True, blank=True, verbose_name="申诉原因详情")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")
    appeal_img = models.ImageField(upload_to="resource/shens", verbose_name="申诉图片", blank=True)
    appeal_video = models.FileField(upload_to="resource/shens", verbose_name="申诉视频", blank=True)
    # order_real_status= models.IntegerField(default=0, choices=((0,''),
    #                                                         (1,'买方付款,卖方线下未背书,买方发起申诉,买方违约,扣买方违约金,返回冻结资金'),
    #                                                         (2,'买方付款,卖方线下未背书,卖方发起申诉,卖方违约,扣卖方违约金,返回冻结资金'),
    #                                                         (3,'买方付款,卖方线下背书,买方不签收,买方发起申诉,买方违约,扣买方违约金,返回冻结资金'),
    #                                                         (4,'买方付款,卖方线下背书,买方不签收,卖方发起申诉,卖方违约,扣卖方违约金,返回冻结资金'),
    #                                                         (5,'买方付款,卖方线下背书,买方签收,买方发起申诉,买方违约,冻结资金划到卖方账户下')))

    solver = models.CharField(max_length=32, null=True, blank=True, verbose_name="申诉处理者")
    solved_time = models.DateTimeField(default=datetime.now, verbose_name="解决时间")
    # solved_result = models.IntegerField(default=0, choices=((0,''),
    #                                                         (1,'买方付款,卖方线下未背书,买方发起申诉,买方违约,扣买方违约金,返回冻结资金'),
    #                                                         (2,'买方付款,卖方线下未背书,卖方发起申诉,卖方违约,扣卖方违约金,返回冻结资金'),
    #                                                         (3,'买方付款,卖方线下背书,买方不签收,买方发起申诉,买方违约,扣买方违约金,返回冻结资金'),
    #                                                         (4,'买方付款,卖方线下背书,买方不签收,卖方发起申诉,卖方违约,扣卖方违约金,返回冻结资金'),
    #                                                         (5,'买方付款,卖方线下背书,买方签收,买方发起申诉,买方违约,冻结资金划到卖方账户下'),
    #                                                         (6,'继续交易')))
    solved_result = models.IntegerField(default=0, choices=((0, ''),
                                                            (1, '扣买方保证金,分账30%平台,70%卖方'),
                                                            (2, '扣卖方保证金,分账30%平台,70%买方'),
                                                            (3, '扣买方保证金,退买方票款(支付了票款买方毁约)'),
                                                            (4, '扣卖方保证金,退买方票款(支付了票款卖方票没了)'),
                                                            (5, '买家未确认签收,划票款给卖方'),
                                                            (6, '继续交易')))

    class Meta:
        verbose_name = "订单申诉仲裁"
        verbose_name_plural = verbose_name


# 消息通知部分
class Notice(models.Model):
    msgtime = models.DateTimeField(default=datetime.now, verbose_name="消息时间")
    msgtype = models.CharField(max_length=10, default="sys", verbose_name="消息类型",
                               choices=(("sys", "系统消息"), ('buyerr', u'买家订单消息'), ("seller",
                                                                                 "卖家订单消息"), ('other', "其他消息")))
    msg = models.CharField(max_length=100, default="", verbose_name="消息内容")
    user = models.CharField(max_length=128, null=True, verbose_name="接收人")
    gongsi = models.ForeignKey(GongSi, null=True, related_name="msg_to_gongsi", verbose_name="接收人所属公司",
                               on_delete=models.CASCADE)
    status = models.CharField(max_length=10, default="unread", choices=(("unread", "未读"), ("readed", "已读")))

    class Meta:
        verbose_name = "通知消息表"
        verbose_name_plural = verbose_name


# 银行调用流水
class BankOrderInfo(models.Model):
    orderno = models.CharField(max_length=32, default="", verbose_name="商户流水号")
    orderdate = models.DateField(default=timezone.now, verbose_name="商户交易日期")
    ordertime = models.DateTimeField(default=datetime.now, verbose_name="商户交易时间")
    funcode = models.CharField(max_length=10, null=False, default="", verbose_name="功能代码")
    retcode = models.CharField(max_length=12, null=False, default="", verbose_name="返回的结果")
    busness = models.CharField(max_length=10, null=False, default="",
                               choices=(("bzj_pay", "付保证金"), ("order_pay", "购票预付款"), ("bzj_refund", "返还保证金"),
                                        ("bzj_bc", "补偿保证金"), ("other", "其它操作")), verbose_name="业务")
    orderid = models.IntegerField(default=0, verbose_name="业务订单号")
    reqinfo = models.CharField(max_length=1024, null=False, default="", verbose_name="请求body")
    status = models.IntegerField(default=0, choices=((0, "初始状态"), (1, "付款确认")), verbose_name="付款状态")

    class Meta:
        verbose_name = "通知消息表"
        verbose_name_plural = verbose_name


# 卖家应收账款
class SellerAccountReceivable(models.Model):
    orderid = models.IntegerField(default=0, verbose_name="业务订单号")
    seller = models.CharField(max_length=128, default="", verbose_name="卖方用户id")
    seller_gongsi = models.ForeignKey(GongSi, related_name="actreceivable_seller_gongsi", verbose_name="卖方公司",
                                      default="", on_delete=models.CASCADE)
    buyer_gongsi = models.ForeignKey(GongSi, related_name="actreceivable_buyer_gongsi", verbose_name="买方公司",
                                     default="", on_delete=models.CASCADE)
    addtime = models.DateTimeField(default=datetime.now, verbose_name="添加时间")
    receivable = models.FloatField(default=0, null=False, verbose_name="应收账款")

    class Meta:
        verbose_name = "卖家应收账款"
        verbose_name_plural = verbose_name


class Jindou(models.Model):
    gongsi = models.ForeignKey(GongSi, related_name="jindou_gongsi", verbose_name="公司", on_delete=models.CASCADE)
    total = models.IntegerField(default=0, verbose_name="金豆总数")
    qiandao_time = models.DateTimeField(default=datetime.now, verbose_name="签到时间")
    jindou_reward = models.IntegerField(default=0, verbose_name="奖励金豆")

    class Meta:
        verbose_name = "金豆表"
        verbose_name_plural = verbose_name

    def can_qiandao(self):
        if self.qiandao_time.date() < datetime.today().date():
            return True
        else:
            return False

    def qiandao(self):
        self.total = self.total + 2
        self.qiandao_time = datetime.now()
        self.save()
        return True

    def first_qiandao(self, gongsi):
        self.gongsi = gongsi
        self.total = 2
        self.qiandao_time = datetime.now()
        self.save()
        return True

    def add_jindou(self, addnum):
        self.total = self.total + addnum
        self.save()
        return True

    def dec_jindou(self, decnum):
        if self.total > decnum:
            self.total = self.total - decnum
            return True
        else:
            return False


class Guapiao(models.Model):
    gongsi = models.ForeignKey(GongSi, related_name="Guapiao_gongsi", verbose_name="公司", on_delete=models.CASCADE)
    days = models.IntegerField(default=0, verbose_name="连续挂票天数")
    # isbreak = models.IntegerField(default=0, verbose_name="是否有中断",choices=((0, "中断"), (1, "无中断")))
    guapiao_time = models.DateTimeField(default=datetime.now, verbose_name="挂票时间")

    class Meta:
        verbose_name = "连续挂票"
        verbose_name_plural = verbose_name


class JindouDetail(models.Model):
    gongsi = models.ForeignKey(GongSi, related_name="jindoudetail_gongsi", verbose_name="公司", on_delete=models.CASCADE)
    num = models.IntegerField(default=0, verbose_name="金豆总数")
    source = models.CharField(max_length=30, default="", verbose_name="渠道")
    optime = models.DateTimeField(default=datetime.now, verbose_name="签到时间")
    total = models.IntegerField(default=0, verbose_name="金豆余额")

    class Meta:
        verbose_name = "金豆日志"
        verbose_name_plural = verbose_name

    def savelog(self, gongsi, num, total, source):
        self.gongsi = gongsi
        self.num = num
        self.total = total
        self.source = source
        self.optime = datetime.now()
        self.save()
