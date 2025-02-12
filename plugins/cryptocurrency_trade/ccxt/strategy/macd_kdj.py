# cd /www/server/mdserver-web &&  source bin/activate
# python3 plugins/cryptocurrency_trade/ccxt/strategy/macd_kdj.py run
# python3 plugins/cryptocurrency_trade/ccxt/strategy/macd_kdj.py long


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


pd.set_option('display.max_rows', None)

# import warnings
# warnings.filterwarnings('error')


def getMACD(df, lenght=-60):
    if len(df['close'].values) < 100:
        return False, None

    close_p = df['close'].values
    df['dif'], df['dea'], df['macd'] = talib.MACD(close_p,
                                                  fastperiod=12,
                                                  slowperiod=26,
                                                  signalperiod=9)
    return True, df[lenght:]


def isKdj(last, last_pre):
    # 判断是否是金叉
    if (float(last_pre['macd']) < 0) and (float(last['macd']) > 0):
        return True
    return False


def isDeadFork(last, last_pre):
    # 判断是否是死叉
    if (float(last_pre['macd']) > 0) and (float(last['macd']) < 0):
        return True
    return False


def checkData():
    tag = 'btc'
    tf_frame = '1h'

    data = common.getDataFromDb_DF(tf_frame, tag, 300)

    # print(data)
    b, r = getMACD(data)
    if b:
        # rlen = len(r)
        # r = r.copy()
        # r['dt'] = pd.to_datetime(
        #     r['addtime'], unit='s')

        # r['dt'] = r['dt'].dt.tz_convert('Asia/Shanghai')
        # print(r)
        rlen = len(r)

        t_data = r.tail(2)
        # print(r.tail(2))

        last_pre = t_data.iloc[0]
        last = t_data.iloc[1]

        # print(last_pre)
        # print(last)
        # print(last_pre['addtime'])
        # print(last_pre['open'])
        # print(last_pre['high'])
        # print(last_pre['low'])
        # print(last_pre['close'])

        # print(last['addtime'])
        # print(last['open'])
        # print(last['high'])
        # print(last['low'])
        # print(last['close'])

        now = mw.getDateFromNow()
        if isKdj(last, last_pre):
            msg = now + "|{}|{}|检查到金叉状态!".format(tag, tf_frame)
            common.notifyMsg(msg, tf_frame, tag)
            common.writeLog(msg)

        if isDeadFork(last, last_pre):
            msg = now + "|{}|{}|检查到死叉状态!".format(tag, tf_frame)
            common.notifyMsg(msg, tf_frame, tag)
            common.writeLog(msg)


def run():
    checkData()


def longRun():
    while True:
        checkData()
        time.sleep(3)


if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'run':
        run()
    elif func == 'long':
        longRun()
    else:
        print('error')
