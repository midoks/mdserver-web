import ccxt


import time
import sys
import json
import os
import glob
import threading

import pandas as pd
from decimal import Decimal
from pprint import pprint
from datetime import datetime

# print(os.getcwd())
sys.path.append(os.getcwd() + "/class/core")
import mw

exchange = ccxt.poloniex()


def calc_ClosingPriceWithOutStopLossPrice(open_price, stype='buy', profit=0.5):
    # profit 百分比 %
    v = 0
    vf_len = len(str(open_price).split('.')[1])
    if stype == 'buy':
        v = open_price * (100 + profit) / 100
    else:
        v = open_price * (100 - profit) / 100
    return round(v, vf_len)


def roundVal(price, compare_price):
    price = float(price)
    csplite = str(compare_price).split('.')
    clen = len(csplite)
    if clen == 2:
        vf_len = len(csplite[1])
        return round(price, vf_len)
    return price


def roundValCeil(price, compare_price):
    price = float(price)
    csplite = str(compare_price).split('.')
    clen = len(csplite)
    if clen == 2:
        vf_len = len(csplite[1]) - 1
        return round(price, vf_len)
    return price


def multiply(a1, a2):
    v = Decimal(str(a1)) * Decimal(str(a2))
    return v


def addition(a1, a2):
    v = Decimal(str(a1)) + Decimal(str(a2))
    return v


def subtract(a1, a2):
    v = Decimal(str(a1)) - Decimal(str(a2))
    return v


def divided(a1, a2):
    v = Decimal(str(a1)) / Decimal(str(a2))
    return v


def calc_ClosingPrice(open_price, stop_loss_price, stype='buy', profit=0.5):
    # profit 百分比 %
    v = 0
    vf_len = len(str(open_price).split('.')[1])
    if stype == 'buy':
        v = open_price * (100 + profit) / 100
        diff = open_price - stop_loss_price
        profit_price = open_price + diff * 1.5
        if profit_price > v:
            return round(profit_price, vf_len)
    else:
        v = open_price * (100 - profit) / 100
        diff = stop_loss_price - open_price
        profit_price = open_price - diff * 1.5
        if profit_price < v:
            return round(profit_price, vf_len)
    return round(v, vf_len)


def toDateFromInt(time_unix, tf_format="%Y-%m-%d %H:%M:%S", time_zone="Asia/Shanghai"):
    # 取格式时间
    import time
    os.environ['TZ'] = time_zone
    time_str = time.localtime(time_unix)
    time.tzset()

    return time.strftime(tf_format, time_str)


def getPluginName():
    return 'cryptocurrency_trade'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getConfigData():
    cfg_path = getServerDir() + "/data.cfg"
    if not os.path.exists(cfg_path):
        mw.writeFile(cfg_path, '{}')
    t = mw.readFile(cfg_path)
    return json.loads(t)


def getUserCfgData():
    data = getConfigData()
    if 'user' in data:
        try:
            udata = mw.deDoubleCrypt('mw', data['user'])
            udata = json.loads(udata)
            return udata
        except Exception as e:
            pass
    return []


def initEx():
    data = getUserCfgData()
    # print(data)
    if (len(data) > 0):
        exchange = ccxt.okex({
            "apiKey": data['app_key'],
            "secret":  data['secret'],
            "password": data['password'],
        })
        return exchange
    else:
        print("初始化失败，检查原因!")
    exchange = ccxt.poloniex()
    return exchange


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


def notifyMsg(msg, tf='15m', tag='btc'):
    trigger_time = toUnixTimeSecond(tf)
    return mw.notifyMessage(msg, '量化交易/' + tag, trigger_time)


def makeTableName(input_type="btc", input_tf="1m"):
    table_name = "ct_%s_%s" % (input_type, input_tf,)
    return table_name


def writeLog(log_str):
    if __name__ == "__main__":
        print(log_str)

    log_file = getServerDir() + '/logs/strategy.log'
    mw.writeFileLog(log_str, log_file)
    return True


def writeLogEx(log_str, tag='btc'):
    tag = tag.replace('/', '_')
    # 各种币的详细API日志
    if __name__ == "__main__":
        print(log_str)

    log_file = getServerDir() + '/logs/strategy_' + tag + '.log'
    mw.writeFileLog(log_str, log_file)
    return True


def writeLogErrorEx(log_str, tag='btc'):
    tag = tag.replace('/', '_')
    # 各种币的详细API日志
    if __name__ == "__main__":
        print(log_str)

    log_file = getServerDir() + '/logs/strategy_' + tag + '.err.log'
    mw.writeFileLog(log_str, log_file)
    return True


def pMysqlDb():
    # pymysql
    db = mw.getMyORM()
    data = getConfigData()
    db_data = data['db']

    # print(db_data)
    db.setHost(db_data['db_host'])
    db.setPort(db_data['db_port'])
    db.setUser(db_data['db_user'])
    db.setPwd(db_data['db_pass'])
    db.setDbName(db_data['db_name'])
    return db


def getOnlineData(symbol,  input_tf="15m", limit=200):
    bars = exchange.fetch_ohlcv(symbol, timeframe=input_tf, limit=limit)
    df = pd.DataFrame(bars[:], columns=['timestamp',
                                        'open', 'high', 'low', 'close', 'volume'])
    df['dt'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df


def toDataFrame(data):
    # print(data)
    data = sorted(data, key=lambda x: x["addtime"], reverse=False)

    dfield = ['addtime', 'open', 'high', 'low', 'close']
    v = {}
    for dx in dfield:
        v[dx] = []

    for x in data:
        for i in range(len(x)):
            field = dfield[i]
            # print(i, field)
            v[field].append(x[field])
    # pprint(data)
    frame = pd.DataFrame(v)
    # frame = frame.sort_values(by=['addtime'])

    frame['dt'] = pd.to_datetime(frame['addtime'], unit='s')
    frame.set_index('dt', inplace=True)
    frame.index = frame.index.tz_localize('UTC').tz_convert('Asia/Shanghai')
    return frame


def getDataFromDb(tf="1m", tag='btc', limit=1000):
    tn = makeTableName(tag, tf)
    sql = 'select addtime,open,high,low,close from ' + \
        tn + ' order by addtime desc limit ' + str(limit)

    pdb = pMysqlDb()
    fdata = pdb.query(sql)
    # print(fdata)
    return fdata


def getDataFromDb_DF(tf="5m", tag='btc', limit=1000):
    data = getDataFromDb(tf, tag, limit)
    rdata = toDataFrame(data)
    return rdata


# 消息模板类
class MsgTpl():

    __name = ''
    __strategy_name = ''
    __time_frame = ''
    __content = ''
    __open_time = ''
    __strategy_dt = ''

    __stop_loss_price = ''
    __closing_price = ''
    __open_price = ''

    __msg = ''

    def setName(self, name):
        self.__name = name

    def setStrategyName(self, name):
        self.__strategy_name = name

    def setTimeFrame(self, tf):
        self.__time_frame = tf

    def setContent(self, content):
        self.__content = content

    def setOpenTime(self, time):
        self.__open_time = toDateFromInt(time)

    def setStrategicDt(self, stype='buy'):
        if stype == 'buy':
            self.__strategy_dt = '做多'
        else:
            self.__strategy_dt = '做空'

    def setStopLossPrice(self, price):
        self.__stop_loss_price = price

    def setClosingPrice(self, price):
        self.__closing_price = price

    def setOpenPrice(self, price):
        self.__open_price = price

    def setMsg(self, msg):
        self.__msg = msg

    def toText(self):
        msg = ''
        msg += '名称:' + self.__name + "\n"

        if self.__strategy_name != '':
            msg += '策略名称:' + self.__strategy_name + "\n"

        if self.__time_frame != '':
            msg += '时间周期:' + self.__time_frame + "\n"

        if self.__content != '':
            msg += '策略描述:' + self.__content + "\n"

        if self.__open_time != '':
            msg += '开盘时间:' + self.__open_time + "\n"

        if self.__strategy_dt != '':
            msg += '开仓方向:' + self.__strategy_dt + "\n"

        if self.__open_price != '':
            msg += '开仓价:' + str(self.__open_price) + "\n"

        if self.__stop_loss_price != '':
            msg += '止损价:' + str(self.__stop_loss_price) + "\n"

        if self.__closing_price != '':
            msg += '止盈价:' + str(self.__closing_price) + "\n"

        msg += '发送时间:' + mw.getDateFromNow() + "\n"

        if self.__msg != '':
            msg += __msg
        return msg
