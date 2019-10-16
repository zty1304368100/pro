MENU = {
    "order_status": [
        {
            "name": "不限",
            "value": "all"
        },
        {
            "name": "待接单",
            "value": "sj"
        },
        {
            "name": "交易中",
            "value": "indeal"
        },
        {
            "name": "交易完成",
            "value": "deal"
        }
    ],
    "piliang" : [
        {
            "name": "不限",
            "value": "all"
        },
        {
            "name": "单张",
            "value": "0"
        },
        {
            "name": "多张",
            "value": "1"
        },
    ]
    ,

    "jiaoyi_type": [
        {
            "name": "不限",
            "value": "all"
        },
        {
            "name": "一口价",
            "value": "ykj"
        },
        {
            "name": "竞价",
            "value": "jj"
        },
        {
            "name": "利率价",
            "value": "llj"
        }
    ]
    ,

    "accepter": [
        {
            "name": "不限",
            "value": "all"
        },
        {
            "name": "银票",
            "value": "yp"
        },
        {
            "name": "财票",
            "value": "cw"
        },
        {
            "name": "商票",
            "value": "sp"
        },
    ]
    ,

    "piaoju_type": [
        {
            "name": "不限",
            "value": "all"
        },
        {
            "name": "国股",
            "value": "gg"
        },
        {
            "name": "城商",
            "value": "cs"
        },
        {
            "name": "三农",
            "value": "sn"
        }, {
            "name": "村镇",
            "value": "cz"
        },
        {
            "name": "其他",
            "value": "other"
        }
    ]
    ,

    "pm_amount": [
        {
            "name": "不限",
            "value": "all"
        },
        {
            "name": "10万以下",
            "value": "0-10"
        },
        {
            "name": "10万-50万",
            "value": "10-50"
        },
        {
            "name": "50万-100万",
            "value": "50-100"
        },
        {
            "name": "100万以上",
            "value": "100-00"
        },
    ]
    ,

    "date_due": [
        {
            "name": "不限",
            "value": "all"
        },
        {
            "name": "90天以内",
            "value": "0-90"
        },
        {
            "name": "91天-160天",
            "value": "91-160"
        },
        {
            "name": "161天-185天",
            "value": "161-185"
        },
        {
            "name": "186天-330天",
            "value": "186-330"
        },
        {
            "name": "331天及以上",
            "value": "331-00"
        },

    ]
    ,

    "flaw_type": [
        {
            "name": "不限",
            "value": "all"
        },
        {
            "name": "无瑕疵",
            "value": "no"
        },
        {
            "name": "重复背书",
            "value": "cf"
        },
        {
            "name": "回头",
            "value": "ht"
        },
        {
            "name": "上下不一致",
            "value": "byz"
        },
        {
            "name": "其他",
            "value": "other"
        }
    ]
    # ,
    # "qiye_type": [
    #     {
    #         "name": "不限",
    #         "value": "all"
    #     },
    #     {
    #         "name": "上市",
    #         "value": "ss"
    #     },
    #     {
    #         "name": "央企",
    #         "value": "yq"
    #     },
    #     {
    #         "name": "国企",
    #         "value": "gq"
    #     },
    #     {
    #         "name": "其他",
    #         "value": "other"
    #     }
    # ]
    ,
    "qiye_category": [
        {
            "name": "不限",
            "value": "all"
        },
        {
            "name": "地产",
            "value": "dc"
        },
        {
            "name": "机械制造",
            "value": "jx"
        },
        {
            "name": "化工",
            "value": "hg"
        },
        {
            "name": "建工",
            "value": "jg"
        },
        {
            "name": "航天军工",
            "value": "ht"
        },
        {
            "name": "其他",
            "value": "other"
        }
    ]
    ,
    "qiye_name": [
        {
            "name": "不限",
            "value": "all"
        },
        {
            "name": "恒大",
            "value": "hd"
        },
        {
            "name": "金科",
            "value": "jk"
        },
        {
            "name": "融创",
            "value": "rc"
        },
        {
            "name": "荣盛",
            "value": "rs"
        },
        {
            "name": "碧桂园",
            "value": "bgy"
        },
        {
            "name": "龙湖",
            "value": "lh"
        },
        {
            "name": "绿地",
            "value": "ld"
        },
        {
            "name": "华夏幸福",
            "value": "hxxf"
        },
        {
            "name": "其他",
            "value": "other"
        }
    ]
}

# 银票或者商票的上传的menu
UPLOAD_MENU = {
    "accepter": [

        {
            "name": "银票",
            "value": "yp"
        },

        {
            "name": "商票",
            "value": "sp"
        },
    ]
    ,
    "jiaoyi_type": [

        {
            "name": "一口价",
            "value": "ykj"
        },
        {
            "name": "竞价",
            "value": "jj"
        },
        {
            "name": "利率价",
            "value": "llj"
        },
    ]
    ,
    "flaw_type": [
        {
            "name": "无瑕疵",
            "value": "no"
        },
        {
            "name": "重复背书",
            "value": "cf"
        },
        {
            "name": "回头",
            "value": "ht"
        },
        {
            "name": "上下不一致",
            "value": "byz"
        },
        {
            "name": "其他",
            "value": "other"
        }
    ]
    ,
    "qiye_category": [

        {
            "name": "地产",
            "value": "dc"
        },
        {
            "name": "机械制造",
            "value": "jx"
        },
        {
            "name": "化工",
            "value": "hg"
        },
        {
            "name": "建工",
            "value": "jg"
        },
        {
            "name": "航天军工",
            "value": "ht"
        },
        {
            "name": "其他",
            "value": "other"
        }
    ]
    ,
    "qiye_name": [
        {
            "name": "恒大",
            "value": "hd"
        },
        {
            "name": "金科",
            "value": "jk"
        },
        {
            "name": "融创",
            "value": "rc"
        },
        {
            "name": "荣盛",
            "value": "rs"
        },
        {
            "name": "碧桂园",
            "value": "bgy"
        },
        {
            "name": "龙湖",
            "value": "lh"
        },
        {
            "name": "绿地",
            "value": "ld"
        },
        {
            "name": "华夏幸福",
            "value": "hxxf"
        },
        {
            "name": "其他",
            "value": "other"
        }
    ]
}

LEFT_MENU = {

}

ORDER_MENU = {

    "order_time": [{'name': "最新订单", 'value': "today_order"},
                   {'name': "历史订单", 'value': "history_order"}
                   ],

    "today_order_status": [{'name': "全部订单", 'value': 'all'},
                           {'name': "待接单", 'value': '1-2','number':0},
                           {'name': "保证金状态", 'value': '3','number':0},
                           {'name': "待打款", 'value': '4','number':0},
                           {'name': "待背书", 'value': '5','number':0},
                           {'name': "待签收", 'value': '6','number':0},
                           {'name': "交易完成", 'value': '7'},
                           {'name': "已取消", 'value': '8'},
                           ],

    "history_order_status": [{'name': "全部订单", 'value': 'all'},
                             {'name': "已完成", 'value': '7'},
                             {'name': "已取消", 'value': '8'},
                             ]
}

TICKET_MENU = {
    "ticket_status": [
        {'name': "当日票据", 'value': "today_piaoju"},
        {'name': "历史票据", 'value': "history_piaoju"}
                   ],
}