# cd /www/server/mdserver-web &&  source bin/activate
# python3 plugins/cryptocurrency_trade/ccxt/strategy/momentun_trade.py run
# python3 plugins/cryptocurrency_trade/ccxt/strategy/momentun_trade.py long


# 动量策略交易

import ccxt
import talib

import sys
import os
import time
import json
import pandas as pd
# import pandas_ta as ta
from pprint import pprint
import numpy as np

sys.path.append(os.getcwd() + "/plugins/cryptocurrency_trade/strategy")
import common

sys.path.append(os.getcwd() + "/class/core")
import mw

exchange = common.initEx()
exchange.load_markets()

# 默认开仓数据
# default_open_num = 70
# default_sell_num = 0.003

default_open = {
    'BTC/USDT': 30,
    'XRP/USDT': 30,
}

default_sell = {
    'BTC/USDT': 0.001,
    'XRP/USDT': 100,
}


# 做多开仓
def onBuyOrderTry(symbol, stop_loss_price, profit=0.005, timeframe='15m'):

    # 信号只在一个周期内执行一次|start
    lock_file = common.getServerDir() + '/signal.json'
    if not os.path.exists(lock_file):
        mw.writeFile(lock_file, '{}')

    stype = symbol.replace('/', '_') + '_' + timeframe
    trigger_time = common.toUnixTimeSecond(timeframe)
    lock_data = json.loads(mw.readFile(lock_file))
    if stype in lock_data:
        diff_time = time.time() - lock_data[stype]['do_time']
        if diff_time >= trigger_time:
            lock_data[stype]['do_time'] = time.time()
        else:
            return False, 0, 0
    else:
        lock_data[stype] = {'do_time': time.time()}

    mw.writeFile(lock_file, json.dumps(lock_data))
    # 信号只在一个周期内执行一次|end

    common.writeLogEx('------做多----------------------------------', symbol)

    default_open_num = default_open[symbol]
    # 做多开仓 | 市价
    data = exchange.createMarketBuyOrder(
        symbol, default_open_num, {"tdMode": "cross"})

    common.writeLogEx('开仓数据:', symbol)
    common.writeLogEx(json.dumps(data), symbol)

    order_id = data['info']['ordId']
    order_data = exchange.fetchOrder(order_id, symbol)

    common.writeLogEx('订单数据:', symbol)
    common.writeLogEx(json.dumps(order_data), symbol)

    # 实际开场平均价
    open_price = order_data['info']['avgPx']

    # 修正小数点位数
    open_price = common.roundVal(open_price, stop_loss_price)
    common.writeLogEx('实际开仓价:' + str(open_price), symbol)

    # 做多-止损价大于开仓价,重设止损价
    if float(stop_loss_price) <= float(open_price):
        stop_loss_price = float(open_price) * float((1 - 0.003))

    # property_val = float(order_data['info']['accFillSz']) + float(order_data['info']['fee'])

    property_val = common.addition(order_data['info'][
        'accFillSz'], order_data['info']['fee'])
    property_val = float(property_val)
    # 可平仓的数量
    # property_val = common.roundValCeil(
    #     property_val, order_data['info']['accFillSz'])

    common.writeLogEx('可平仓资产:' + str(property_val), symbol)

    # 止盈价
    diff = float(open_price) - float(stop_loss_price)
    closing_price = float(open_price) + (diff * 1.5)
    # closing_price = float(open_price) * float((1 + profit))
    # # 选择盈利多的
    # if closing_price_c > closing_price:
    #     closing_price = closing_price_c

    closing_price = common.roundVal(closing_price, open_price)
    stop_loss_price = common.roundVal(stop_loss_price, open_price)
    common.writeLogEx('止盈价:' + str(closing_price), symbol)
    common.writeLogEx('止损价:' + str(stop_loss_price), symbol)

    # 设置 - 止损价/止盈价
    sl_exchange_params = {
        'ccy': "USDT",
        'reduceOnly': True,
        'tdMode': "cross",
        'slOrdPx': "-1",
        'slTriggerPx': stop_loss_price,
    }

    # 止损条件单
    common.writeLogEx('止损参数:' + json.dumps([symbol, 'limit', 'sell',
                                            property_val, stop_loss_price, sl_exchange_params]), symbol)
    sl_cond_data = exchange.create_order(
        symbol, 'limit', 'sell', property_val, stop_loss_price, sl_exchange_params)

    common.writeLogEx('止损价数据:', symbol)
    common.writeLogEx(json.dumps(sl_cond_data), symbol)

    # 止赢条件单
    tp_exchange_params = {
        'ccy': "USDT",
        'reduceOnly': True,
        'tdMode': "cross",
        'tpOrdPx': "-1",
        'tpTriggerPx': closing_price,
    }
    common.writeLogEx('止盈参数:' + json.dumps([symbol, 'limit', 'sell',
                                            property_val, closing_price, tp_exchange_params]), symbol)
    tp_cond_data = exchange.create_order(
        symbol, 'limit', 'sell', property_val, closing_price, tp_exchange_params)

    common.writeLogEx('止盈数据:', symbol)
    common.writeLogEx(json.dumps(tp_cond_data), symbol)

    common.writeLogEx('------做多 end----------------------------------', symbol)
    return True, open_price, closing_price


def onBuyOrder(symbol, stop_loss_price, profit=0.005, timeframe='15m'):
    # 做多开仓
    # profit 百分比
    try:
        return onBuyOrderTry(symbol, stop_loss_price, profit, timeframe)
    except Exception as e:
        common.writeLogErrorEx(mw.getTracebackInfo(), symbol)
        return False, 0, 0


def onSellOrderTry(symbol, stop_loss_price, profit=0.005, timeframe='15m'):

    # 信号只在一个周期内执行一次|start
    lock_file = common.getServerDir() + '/signal.json'
    if not os.path.exists(lock_file):
        mw.writeFile(lock_file, '{}')

    stype = symbol.replace('/', '_') + '_' + timeframe
    trigger_time = common.toUnixTimeSecond(timeframe)
    lock_data = json.loads(mw.readFile(lock_file))
    if stype in lock_data:
        diff_time = time.time() - lock_data[stype]['do_time']
        if diff_time >= trigger_time:
            lock_data[stype]['do_time'] = time.time()
        else:
            return False, 0, 0
    else:
        lock_data[stype] = {'do_time': time.time()}

    mw.writeFile(lock_file, json.dumps(lock_data))
    # 信号只在一个周期内执行一次|end
    common.writeLogEx('------做空----------------------------------', symbol)

    # 计算借币卖币多多少,以USDT为基准
    # sell_num = float(default_open_num) / float(stop_loss_price)
    # sell_num = round(sell_num, 8)
    # sell_num = default_sell_num
    sell_num = default_sell[symbol]

    # 做空开仓 | 市价
    data = exchange.createMarketSellOrder(
        symbol, sell_num, {"tdMode": "cross", 'ccy': "USDT"})

    common.writeLogEx('开仓数据:', symbol)
    common.writeLogEx(json.dumps(data), symbol)

    order_id = data['info']['ordId']
    order_data = exchange.fetchOrder(order_id, symbol)

    common.writeLogEx('订单数据:', symbol)
    common.writeLogEx(json.dumps(order_data), symbol)

    # 实际开场平均价
    open_price = order_data['info']['avgPx']

    # 修正
    open_price = common.roundVal(open_price, stop_loss_price)

    common.writeLogEx('实际开仓价:' + str(open_price), symbol)
    common.writeLogEx('可平仓资产:' + str(sell_num), symbol)

    # 做空-止损价小于开仓价,重设止损价
    if float(stop_loss_price) <= float(open_price):
        stop_loss_price = float(open_price) * float((1 + 0.003))

    # 止盈价
    diff = float(stop_loss_price) - float(open_price)
    closing_price = float(open_price) - (diff * 1.5)
    # closing_price = float(open_price) * float((1 - profit))
    # 选择盈利多的
    # if closing_price_c < closing_price:
    # closing_price = closing_price_c

    closing_price = common.roundVal(closing_price, open_price)
    stop_loss_price = common.roundVal(stop_loss_price, open_price)

    common.writeLogEx('止盈价:' + str(closing_price), symbol)
    common.writeLogEx('止损价:' + str(stop_loss_price), symbol)

    # 设置 - 止损价
    sl_exchange_params = {
        'ccy': "USDT",
        'reduceOnly': True,
        'tdMode': "cross",
        'slOrdPx': "-1",
        'slTriggerPx': stop_loss_price,
    }

    sl_amount = common.multiply(stop_loss_price, sell_num)
    # 解决平仓时,未全部平仓
    sl_amount = common.addition(sl_amount, 0.1)
    common.writeLogEx('止损总价值:' + str(sl_amount), symbol)
    common.writeLogEx('止损参数:' + json.dumps([symbol, 'limit', 'buy', float(
        sl_amount), stop_loss_price, sl_exchange_params]), symbol)
    sl_cond_data = exchange.create_order(
        symbol, 'limit', 'buy', float(sl_amount), stop_loss_price, sl_exchange_params)

    common.writeLogEx('止损价数据:', symbol)
    common.writeLogEx(json.dumps(sl_cond_data), symbol)

    tp_exchange_params = {
        'ccy': "USDT",
        'reduceOnly': True,
        'tdMode': "cross",
        'tpOrdPx': "-1",
        'tpTriggerPx': closing_price,
    }

    # 设置 -止盈价
    # tp_amount = closing_price * sell_num
    tp_amount = common.multiply(closing_price, sell_num)
    # 解决平仓时,未全部平仓
    tp_amount = common.addition(tp_amount, 0.1)
    common.writeLogEx('止盈总价值:' + str(tp_amount), symbol)
    common.writeLogEx('止盈参数:' + json.dumps([symbol, 'limit', 'buy', float(
        tp_amount), closing_price, tp_exchange_params]), symbol)
    tp_cond_data = exchange.create_order(
        symbol, 'limit', 'buy', float(tp_amount), closing_price, tp_exchange_params)

    common.writeLogEx('止盈价数据:', symbol)
    common.writeLogEx(json.dumps(tp_cond_data), symbol)

    common.writeLogEx('------做空 end----------------------------------', symbol)
    return True, open_price, closing_price


def onSellOrder(symbol, stop_loss_price, profit=0.005, timeframe='15m'):
    # 做空开仓
    # profit 百分比
    try:
        return onSellOrderTry(symbol, stop_loss_price, profit, timeframe)
    except Exception as e:
        common.writeLogErrorEx(mw.getTracebackInfo(), symbol)
        return False, 0, 0


def getOnlineData(symbol,  input_tf="15m", limit=230):
    bars = exchange.fetch_ohlcv(symbol, timeframe=input_tf, limit=limit)
    df = pd.DataFrame(bars[:], columns=['timestamp',
                                        'open', 'high', 'low', 'close', 'volume'])
    df['dt'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('dt', inplace=True)
    df.index = df.index.tz_localize('UTC').tz_convert('Asia/Shanghai')
    return df


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


def getMACD(df, lenght=-60):
    if len(df['close'].values) < 100:
        return False, None

    close_p = df['close'].values
    df['dif'], df['dea'], df['macd'] = talib.MACD(close_p,
                                                  fastperiod=12,
                                                  slowperiod=26,
                                                  signalperiod=9)
    return df[lenght:]


def getTarget(df):
    close = df['close'].values
    df['ema'] = talib.EMA(np.array(close), timeperiod=10)
    df['ema_200'] = talib.EMA(np.array(close), timeperiod=200)
    df['ma'] = talib.MA(close, timeperiod=10)
    df['rsi'] = talib.RSI(close, timeperiod=14)
    return df


# 多头信号
def isBuyCrondSignal(last):
    if last['ema'] > last['ma'] and (last['rsi'] > 50 and last['rsi'] < 70) and last['low'] >= last['ma'] and last['close'] > last['open']:
        return True
    return False


def isBuyFristSignal(data):
    data = data.sort_values(by=['timestamp'], ascending=False)
    # print(data)
    data_len = len(data)
    signal_num = 0

    first_data = data.iloc[1]
    # print(1, first_data['close'], first_data['ema'])
    is_buy_signal = isBuyCrondSignal(first_data)

    for x in range(2, data_len):
        tmp = data.iloc[x]
        # print(data.iloc[x])
        # print(x, tmp['close'], tmp['ema'])
        if isBuyCrondSignal(tmp):
            signal_num = + 1

        # print('signal_num:', signal_num)

        if (tmp['ema'] < tmp['ma']):
            break

        if str(tmp['ema']) == 'nan':
            break

    print("is_buy_signal:", is_buy_signal, 'signal_num:', signal_num)
    if is_buy_signal and signal_num == 0:
        return True

    return False


# 空头信号
def isSellCrondSignal(last):
    if last['ema'] < last['ma'] and (last['rsi'] > 30 and last['rsi'] < 50) and last['high'] <= last['ema'] and last['close'] < last['open']:
        return True
    return False


def isSellFristSignal(data):
    data = data.sort_values(by=['timestamp'], ascending=False)
    # print(data)
    data_len = len(data)
    signal_num = 0

    first_data = data.iloc[1]
    # print(1, first_data['close'], first_data['ema'])
    is_sell_signal = isSellCrondSignal(first_data)

    for x in range(2, data_len):
        tmp = data.iloc[x]
        # print(data.iloc[x])
        # print(x, tmp['close'], tmp['ema'])
        if isSellCrondSignal(tmp):
            signal_num = + 1

        # print('signal_num:', signal_num)

        if (tmp['ema'] < tmp['ma']):
            break

        if str(tmp['ema']) == 'nan':
            break

    print("is_sell_signal:", is_sell_signal, 'signal_num:', signal_num)
    if is_sell_signal and signal_num == 0:
        return True

    return False


def monentunTrade(data, tag, timeframe):
    data = getTarget(data)
    # print(data)

    key_data = data.tail(3)
    print(key_data)
    last_pre = key_data.iloc[0]
    last = key_data.iloc[1]

    obj = common.MsgTpl()
    symbol = tag.upper() + '/USDT'
    obj.setName(symbol)
    obj.setStrategyName("动量交易策略")
    obj.setTimeFrame(timeframe)
    obj.setOpenTime(last['timestamp'] / 1000)

    # 买入信号，并且收盘价要大于200 ema
    if isBuyFristSignal(data) and last['close'] > last['ema_200']:
        obj.setStrategicDt('buy')

        # 做多止损点
        stop_loss_price = last['ma']
        stop_loss_price = common.roundVal(stop_loss_price, last['open'])
        buy_status, open_price, closing_price = onBuyOrder(
            symbol, stop_loss_price, 0.005, timeframe)

        if buy_status:
            # 做多止损点
            obj.setStopLossPrice(str(stop_loss_price))
            obj.setOpenPrice(str(open_price))
            obj.setClosingPrice(str(closing_price))
            obj.setContent("动量交易策略做多!")
            msg = obj.toText()
            print(msg)
            common.notifyMsg(msg, timeframe, tag)
            common.writeLog(msg)

    # 卖出信号，并且收盘价要小于200 ema
    # if isSellFristSignal(data) and last['close'] < last['ema_200']:
    #     obj.setStrategicDt('sell')

    #     stop_loss_price = last['ma']
    #     stop_loss_price = common.roundVal(stop_loss_price, last['open'])
    #     sell_status, open_price, closing_price = onSellOrder(
    #         symbol, stop_loss_price, 0.005, timeframe)
    #     if sell_status:
    #         obj.setStopLossPrice(str(stop_loss_price))
    #         obj.setOpenPrice(str(open_price))
    #         obj.setClosingPrice(str(closing_price))
    #         obj.setStrategicDt('sell')
    #         obj.setContent("动量交易策略作空!")
    #         msg = obj.toText()
    #         print(msg)
    #         common.notifyMsg(msg, timeframe, tag)
    #         common.writeLog(msg)


def mainProcess(tag, timeframe='15m'):
    symbol = tag.upper() + '/USDT'
    data = getOnlineData(symbol, timeframe)

    monentunTrade(data, tag, timeframe)


def foreachList():
    tag_list = ['btc', 'xrp']
    for tag in tag_list:
        mainProcess(tag, '15m')
        time.sleep(1)


def longRun():
    while True:
        foreachList()
        time.sleep(1)


def debug():
    while True:
        mainProcess('btc', '5m')
        time.sleep(1)


if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'long':
        longRun()
    elif func == 'run':
        debug()
    else:
        print('error')
