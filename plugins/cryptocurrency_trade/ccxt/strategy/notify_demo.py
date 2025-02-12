# cd /www/server/mdserver-web &&  source bin/activate
# python3 plugins/cryptocurrency_trade/ccxt/strategy/notify_demo.py run
# python3 plugins/cryptocurrency_trade/ccxt/strategy/notify_demo.py long


import ccxt
import talib
import pandas as pd
import time

import sys
import os
from pprint import pprint

sys.path.append(os.getcwd() + "/plugins/cryptocurrency_trade/strategy")
import common

sys.path.append(os.getcwd() + "/class/core")
import mw


def run():
    print('debug')


def longRun():
    while True:

        obj = common.MsgTpl()
        obj.setName("通知测试")
        obj.setStrategyName("无")
        obj.setTimeFrame("1m")
        obj.setContent("60s通知测试")
        msg = obj.toText()
        print(msg)
        common.notifyMsg(msg, '1m', 'debug')
        common.writeLog(msg)
        time.sleep(3)


if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'run':
        run()
    if func == 'long':
        longRun()
    else:
        print('error')
