import ccxt
import talib

import sys
import os
import time
import pandas as pd
import pandas_ta as ta
from pprint import pprint

sys.path.append(os.getcwd() + "/plugins/cryptocurrency_trade/strategy")
import common

# cd /www/server/mdserver-web &&  source bin/activate
# python3 plugins/cryptocurrency_trade/ccxt/strategy/rsi_robot.py run


pd.set_option('display.max_rows', None)

exchange = common.initEx()

# 查看隐形方法
# print(dir(exchange))


exchange.load_markets()

entry_rsi = 30
exit_rsi = 40


symbol = 'XRP/USDT'
timeframe = '15m'

tf_mult = exchange.parse_timeframe(timeframe) * 1000


def indicators(data):

    data['rsi'] = data.ta.rsi(length=10)
    data['ema'] = data.ta.ema(length=200)

    # close_p = data['close'].values
    # data['rsi'] = talib.RSI(close_p, timeperiod=10)
    # data['ema'] = talib.EMA(close_p, timeperiod=200)
    return data


def check_buy_sell_signals(df):
    last_row_index = len(df.index) - 1
    lastest_rsi = round(df['rsi'].iloc[-1], 2)
    lastest_price = round(df['close'].iloc[-1], 5)
    lastest_ema = round(df['ema'].iloc[-1], 5)
    lastest_ts = df['timestamp'].iloc[-1]

    msg = "lastest_rsi:" + str(lastest_rsi) + " < entry_rsi:" + str(entry_rsi)
    msg += ",lastest_price:" + \
        str(lastest_price) + " > lastest_ema:" + str(lastest_ema)
    print(msg)

    long_cond = (lastest_rsi < entry_rsi) and (lastest_price > lastest_ema)
    if long_cond:
        print("买入")
        order = exchange.create_market_buy_order(symbol, 1)

    closed_orders = exchange.fetchClosedOrders(symbol, limit=2)
    if len(closed_orders) > 0:
        print("closed_orders:", closed_orders)
        most_recent_closed_order = closed_orders[-1]
        diff = lastest_ts - most_recent_closed_order['timestamp']
        last_buy_signal_cnt = int(diff / tf_mult)

        exit_cond = (lastest_rsi > exit_rsi) and (last_buy_signal_cnt > 10)
        if exit_cond:
            print("卖出")
            order = exchange.create_market_sell_order(symbol, 1)
        return


def runBot():
    bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=200)
    df = pd.DataFrame(bars[:], columns=['timestamp',
                                        'open', 'high', 'low', 'close', 'volume'])
    df['dt'] = pd.to_datetime(df['timestamp'], unit='ms')

    df = indicators(df).tail(30)

    check_buy_sell_signals(df)


def longRunBot():
    while True:
        runBot()
        time.sleep(10)


if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'run':
        longRunBot()
    else:
        print('error')
