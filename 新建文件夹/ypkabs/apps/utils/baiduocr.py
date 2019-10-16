# --*-- encoding:utf-8 --*--
import sys
import json



hanzi_str = "壹 贰 叁 肆 伍 陆 柒 捌 玖 零 一 二 三 四 五 六 七 八 九 〇 参"
danwei1_str = "亿万仟佰拾元十百千角分"
shuzi_str = "1234567890"
zhnum = {u"壹": 1, u"贰": 2, u"叁": 3, u"肆": 4, u"伍": 5, u"陆": 6, u"柒": 7, u"捌": 8, u"玖": 9, u"零": 0, u'一': 1, u'二': 2,
         u'三': 3, u'四': 4, u'五': 5, u'六': 6, u'七': 7, u'八': 8, u'九': 9, u'〇': 0, u'参': 3}
beishu = {u"元": 1, u"拾": 10, u"佰": 100, u"仟": 1000, u"万": 10000, u"亿": 100000000, u"角": 0.1, u"分": 0.01, u'十': 10,
          u'百': 100, u'千': 1000}

def DX2XX(z):
    # 去掉非法字符
    # if
    z = z.replace('人民币','').replace('(','').replace(')','').replace(':','').replace('大写','').replace('人民巿','').replace('人民市','').replace('票据金额','')
    if len(z) == 0:
        return 0
    z = z.replace("貮", "二")
    s = z
    u_hanzi_str = hanzi_str
    u_danwei1_str = danwei1_str
    if s[0] not in u_hanzi_str:
        print("xxx")
        return 0

    weizhi = []
    pre_shuzi = False

    for i in s:
        # print "++++++++++++++++++++++++++", i
        if i in u_hanzi_str:
            weizhi.append(zhnum[i])
            pre_shuzi = True
        if i in u_danwei1_str:
            if i == "万" or i == "亿":
                for j in range(len(weizhi)):
                    weizhi[j] = int(weizhi[j]) * beishu[i]
                    # print weizhi[j]
            else:
                # print weizhi[-1]
                # print beishu[i]
                if i == "拾" or i == "佰" or i == "仟":
                    if pre_shuzi == False:
                        continue
                weizhi[-1] = int(weizhi[-1]) * beishu[i]
            pre_shuzi = False

    # print weizhi
    total = 0
    for k in range(len(weizhi)):
        total = total + weizhi[k]
    print(total)
    return total


from aip import AipOcr

"""  APPID AK SK """
APP_ID = '17033038'
API_KEY = 'vKgjB0UsqScDCIuPwyiGpGzD'
SECRET_KEY = ' D1A7W3fyjPYBus0FKVOIU5KMx6cxXk0m'

client = AipOcr(APP_ID, API_KEY, SECRET_KEY)




def img_text(filepath):

    def get_file_content(filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()

    image = get_file_content(filepath)

    client.receipt(image)

    options = {}
    # options["detect_direction"] = "true"
    # options["probability"] = "true"
    options["recognize_granularity"] = "big"
    options["probability"] = "true"
    options["accuracy"] = "normal"
    options["detect_direction"] = "true"
    options["verify"] = "false"
    res = client.receipt(image, options)
    # print res
    # print(res['words_result_num'])
    # print(res['words_result'])


    # index = 0
    # for msg in res['words_result']:
    #     print index,msg['words']
    #     index += 1


    date_daoqi = ""
    ticket_money = 0.0
    ticket_number = ""
    chengduiren_msg = ""
    chengduiren_msg2 = ""
#round 1
    for msg in res['words_result']:
        if msg['words'].__contains__('汇票到期'):
            date_daoqi= msg['words'].replace('曰','日').split('日')[1].replace(':','')
        elif msg['words'].__contains__('票据号码')  or msg['words'].__contains__('票据编号'):
            ticket_number = msg['words'].replace(':','').replace("票据号码","").replace("票据编号","")
        elif msg['words'].__contains__('大写') or msg['words'].__contains__('人民币') or msg['words'].__contains__('人民市') or msg['words'].__contains__('人民巿'):
            if ticket_money == 0.0:
                ticket_money = DX2XX(msg['words'])
        elif msg['words'].__contains__('承兑人信息'):
            if msg['words'].__contains__('全称'):
                chengduiren_msg = msg['words'].split('全称')[1]
            else:
                chengduiren_index = res['words_result'].index(msg)-2
                tmpmsg = res['words_result'][chengduiren_index]['words']
                if tmpmsg.__contains__("全称"):
                    chengduiren_msg = tmpmsg.split('称')[1]
        elif msg['words'].__contains__('承兑人名称'):
            chengduiren_msg = msg['words'].split('称')[1].replace(':','')
        elif msg['words'].__contains__("开户行名称"):
            chengduiren_msg2 = msg['words'].split('名称')[1]

#round 2
    if date_daoqi == "" or ticket_number == "" or chengduiren_msg == "": 
        for msg in res['words_result']:
            if date_daoqi == "" and msg['words'].__contains__('汇票到期'):
                idx = res['words_result'].index(msg)+1 
                tmp = res['words_result'][idx]['words']
                if tmp.__contains__('-') and tmp.__contains__("20"):
                    date_daoqi = tmp 
            if ticket_number == "" and (msg["words"].__contains__('票据号码') or msg["words"].__contains__('票号')): 
                idx = res['words_result'].index(msg)+1
                tmp = res['words_result'][idx]['words']
                if len(tmp) == 30: 
                    ticket_number = tmp 
            if chengduiren_msg2 == "" and msg["words"].__contains__("开户行名称"):
                idx = res['words_result'].index(msg)+1
                tmp = res['words_result'][idx]['words']
                chengduiren_msg2 = tmp 

    if chengduiren_msg == "":
        chengduiren_msg = chengduiren_msg2

    print('到期日:'+date_daoqi)
    print('票号:'+ticket_number)
    print('票据金额:'+str(ticket_money))
    print('承兑人:'+chengduiren_msg)

    return date_daoqi,ticket_number,ticket_money,chengduiren_msg


# if __name__ == '__main__':
#     img_text('a0fde89d80c9ae019d685e0543713299.jpg')


def bankcard_orc(filepath):

    def get_file_content(filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()
    image = get_file_content(filepath)

    # """ 调用银行卡识别 """
    res = client.bankcard(image)
    # print res
    if res.get('error_msg','') == '':

        bank_card_number = res['result']['bank_card_number']
        valid_date = res['result']['valid_date']
        bank_card_type = res['result']['bank_card_type']
        bank_name = res['result']['bank_name']
        return bank_card_number,valid_date,bank_card_type,bank_name

    else:
        return u'recognize bank card error'
