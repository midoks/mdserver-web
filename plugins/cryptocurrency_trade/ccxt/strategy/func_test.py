# import ccxt
# import talib

import sys
import os
import time
# import pandas as pd
from pprint import pprint
from decimal import Decimal

sys.path.append(os.getcwd() + "/plugins/cryptocurrency_trade/strategy")
import common

# cd /www/server/mdserver-web &&  source bin/activate
# python3 plugins/cryptocurrency_trade/ccxt/strategy/func_test.py run

# common.notifyMsg("任务开始")


def toUnixTimeSecond(tf="1m"):
    if tf.find("m") > -1:
        v = int(tf.replace("m", ''))
        return v * 60

    if tf.find("h") > -1:
        v = int(tf.replace("h", ''))
        return v * 3600

    if tf.find("d") > -1:
        v = int(tf.replace("d", ''))
        return v * 86400
    return 0


def multiply(a1, a2):
    v = Decimal(str(a1)) * Decimal(str(a2))
    return v

# print(toUnixTimeSecond("1d"))

# f = 19911.2
# s = common.calc_ClosingPrice(f, 19890.2, 'buy')
# print(s)

# print(sys.version_info)
# os.environ['TZ'] = 'Europe/London'
# time.tzset()
# t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
# print(t)

# v = multiply(26236.8, 0.003)
# print(float(v))
# print(v)

print(float('0.00255234') + float('-0.00000255234'))
v1 = common.addition('0.00255234', '-0.00000255234')
print(v1)
