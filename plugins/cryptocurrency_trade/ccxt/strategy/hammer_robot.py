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
# python3 plugins/cryptocurrency_trade/ccxt/strategy/hammer_robot.py run


pd.set_option('display.max_rows', None)

exchange = common.initEx()

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


def get_hammer(df, lenght):
    # 影线要大于body的多少倍
    factor = 2
    hl_range = df['high'] - df['low']

    body_hi = df.apply(lambda x: max(x['close'], x['open']), axis=1)
    body_lo = df.apply(lambda x: min(x['close'], x['open']), axis=1)
    body = body_hi - body_lo

    body_avg = ta.ema(body, lenght=lenght)
    small_body = body < body_avg

    # 上下影线站body的百分比
    shadow_percent = 10

    # 上影线
    up_shadow = df['high'] - body_hi
    dn_shadow = body_lo - df['low']
    has_up_shadow = up_shadow > shadow_percent / 100 * body
    has_dn_shadow = dn_shadow > shadow_percent / 100 * body

    downtrend = df['close'] < ta.ema(df['close'], 50)
    bullish_hammer = downtrend & small_body & (body > 0) & (
        dn_shadow >= factor * body) & (has_up_shadow == False)
    return bullish_hammer


def runBot():
    bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=200)
    df = pd.DataFrame(bars[:], columns=['timestamp',
                                        'open', 'high', 'low', 'close', 'volume'])

    # format='%Y-%m-%d %H:%M:%S',
    df['dt'] = pd.to_datetime(
        df['timestamp'],  unit="ms")

    df['hammer'] = get_hammer(df, 10)

    lastest_hammer = df.iloc[-1, -1]
    lastest_price = df.iloc[-1, 0]

    print("lastest_price:" + str(lastest_price))
    print("lastest_hammer:" + str(lastest_hammer))
    print(df.tail())

    if lastest_hammer:
        print("购买，做多")
        notifyMsg("购买，做多")


def longRunBot():
    common.notifyMsg("任务开始")
    while True:
        runBot()
        time.sleep(10)


if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'run':
        longRunBot()
    else:
        print('error')
