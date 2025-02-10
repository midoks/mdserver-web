# cd /www/server/mdserver-web &&  source bin/activate

# python3 plugins/cryptocurrency_trade/ccxt/strategy/on_g_test.py t_buy_open
# python3 plugins/cryptocurrency_trade/ccxt/strategy/on_g_test.py t_buy_close


# python3 plugins/cryptocurrency_trade/ccxt/strategy/on_g_test.py t_sell_open
# python3 plugins/cryptocurrency_trade/ccxt/strategy/on_g_test.py t_sell_cloe

# 获取仓位数据
# python3 plugins/cryptocurrency_trade/ccxt/strategy/on_g_test.py t_get_trade

# API地址
# https://www.gate.io/docs/developers/apiv4/zh_CN/#api

import ccxt
import talib

import sys
import os
import time
import pandas as pd
# import pandas_ta as ta
from pprint import pprint
import numpy as np

sys.path.append(os.getcwd() + "/plugins/cryptocurrency_trade/strategy")
import common

sys.path.append(os.getcwd() + "/class/core")
import mw

exchange = ccxt.gate({
    "apiKey": '756e1ff80526cb0ac9620c75680fc506',
    "secret":  '95ac89362056bcf12ce37aabff6eb7ec78185483105f39b4a35e8dc8db8b4d3c',
})

exchange.load_markets()


def t_get_trade():
    data = exchange.fetchPositions()
    print(data)


def btc_test():
    closing_price = 24599.9
    stop_loss_price = 24740.4

    # ---------------------------
    stop_loss_args = {
        'ccy': "USDT",
        'reduceOnly': True,
        'tdMode': "cross",
        'slOrdPx': "-1",
        'slTriggerPx': stop_loss_price,
    }
    print('---------止损价 执行 START ----------------------------------')

    sl_amount = stop_loss_price * 0.001
    print(amount)
    data = exchange.create_order(
        'BTC/USDT', 'limit', 'buy', sl_amount, stop_loss_price, stop_loss_args)
    print(data)
    print('---------止损价 执行 END ----------------------------------')

    print('---------止盈价 执行 START ----------------------------------')

    closing_price_args = {
        'ccy': "USDT",
        'reduceOnly': True,
        'tdMode': "cross",
        'tpOrdPx': "-1",
        'tpTriggerPx': closing_price,
    }

    cp_amount = closing_price * 0.001
    print(amount)
    data = exchange.create_order(
        'BTC/USDT', 'limit', 'buy', cp_amount, closing_price, closing_price_args)
    print(data)
    print('---------止盈价 执行 END ----------------------------------')


def testK_buy_open_sz():
    # 做多开仓

    data = exchange.fetchTicker('BTC/USDT')
    print(data)
    # data = exchange.createMarketBuyOrder('DOT/USDT', 1, {"tdMode": "cross"})
    # print(data)
    # print(type(data))


def testK_buy_open():
    # 做多开仓

    # print(dir(exchange))

    # exchange['options']['createMarketBuyOrderRequiresPrice'] = False
    data = exchange.fetch_ticker('BTC/USDT')
    print("now price:", data['ask'])

    amount = 0.001
    price = data['ask']
    cost = amount * float(price)
    print('total price:', cost)
    print('amount price:', amount)
    # a_amount = round(amount / data['ask'], 5)
    # print('amount :', amount)
    # print('amount :', str(amount))

    #
    data = exchange.createOrder(
        "BTC/USDT", type="limit", side="buy", amount=amount,  price=price, params={'account': "cross_margin"})
    # data = exchange.createMarketBuyOrder('BTC/USDT', amount)
    print(data)
    print(type(data))

    # 数据
    # {'info': {'clOrdId': 'e847386590ce4dBC58e8b0afb0fe70cc', 'ordId': '554437054223302656', 'sCode': '0', 'sMsg': 'Order placed', 'tag': 'e847386590ce4dBC'}, 'id': '554437054223302656', 'clientOrderId': 'e847386590ce4dBC58e8b0afb0fe70cc', 'timestamp': None, 'datetime': None, 'lastTradeTimestamp': None, 'symbol': 'DOT/USDT', 'type': 'market', 'timeInForce': None, 'postOnly': None, 'side': 'buy', 'price': None, 'stopPrice': None, 'triggerPrice': None, 'average': None, 'cost': None, 'amount': None, 'filled': None, 'remaining': None, 'status': None, 'fee': None, 'trades': [], 'reduceOnly': None, 'fees': []}

    # 查询委托单
    # order_id = data['info']['ordId']
    # order_id = '554437054223302656'
    # data = exchange.fetchOrder(order_id, 'BTC/USDT')
    # print(data['info'])
    # {'info': {'accFillSz': '0.190548', 'algoClOrdId': '', 'algoId': '', 'avgPx': '5.248', 'cTime': '1678441709955', 'cancelSource': '', 'cancelSourceReason': '', 'category': 'normal', 'ccy': 'USDT', 'clOrdId': 'e847386590ce4dBCeaddfd1494dc7080', 'fee': '-0.000190548', 'feeCcy': 'DOT', 'fillPx': '5.248', 'fillSz': '0.190548', 'fillTime': '1678441709957', 'instId': 'DOT-USDT', 'instType': 'MARGIN', 'lever': '10', 'ordId': '554359943143833600', 'ordType': 'market', 'pnl': '0', 'posSide': 'net', 'px': '', 'quickMgnType': '', 'rebate': '0', 'rebateCcy': 'USDT', 'reduceOnly': 'false', 'side': 'buy', 'slOrdPx': '', 'slTriggerPx': '', 'slTriggerPxType': '', 'source': '', 'state': 'filled', 'sz': '1', 'tag': 'e847386590ce4dBC', 'tdMode': 'cross', 'tgtCcy': '', 'tpOrdPx': '', 'tpTriggerPx': '', 'tpTriggerPxType': '', 'tradeId': '81184616', 'uTime': '1678441709960'}, 'id': '554359943143833600', 'clientOrderId': 'e847386590ce4dBCeaddfd1494dc7080', 'timestamp': 1678441709955, 'datetime': '2023-03-10T09:48:29.955Z', 'lastTradeTimestamp': 1678441709957, 'symbol': 'DOT/USDT', 'type': 'market', 'timeInForce': 'IOC', 'postOnly': None, 'side': 'buy', 'price': 5.248, 'stopPrice': None, 'triggerPrice': None, 'average': 5.248, 'cost': 0.999995904, 'amount': 1.0, 'filled': 0.190548, 'remaining': 0.809452, 'status': 'closed', 'fee': {'cost': 0.000190548, 'currency': 'DOT'}, 'trades': [], 'reduceOnly': False, 'fees': [{'cost': 0.000190548, 'currency': 'DOT'}]}

    # open_price = data['info']['avgPx']
    # print("开仓平均价", open_price)

    # # 止盈价
    # closing_price = float(open_price) * float((1 + 0.005))
    # closing_price = common.roundVal(closing_price, open_price)
    # print("止盈价", closing_price)

    # # 止损价
    # stop_loss_price = float(open_price) * float((1 - 0.01))
    # stop_loss_price = common.roundVal(stop_loss_price, open_price)
    # print("止损价", stop_loss_price)

    # property_val = float(data['info']['accFillSz']) + \
    #     float(data['info']['fee'])

    # # 相同位数
    # property_val = common.roundValCeil(property_val, data['info']['accFillSz'])
    # print("可平仓资产", property_val)

    # closed_orders = exchange.fetchClosedOrders('DOT/USDT', limit=2)
    # print('closed_orders', closed_orders)

    # print(exchange.fetchBalance())

    # 可以用,限价单
    # time.sleep(1)
    # data = exchange.createLimitSellOrder(
    #     'DOT/USDT', property_val, closing_price, {"tdMode": "cross", 'ccy': 'USDT', "reduceOnly": True})
    # print(data)
    # print(type(data))

    # 止损价
    # 止盈价

    # exchange_params = {
    #     'ccy': "USDT",
    #     'reduceOnly': True,
    #     'tdMode': "cross",
    #     'tpOrdPx': "-1",
    #     'tpTriggerPx': closing_price,
    #     'slOrdPx': "-1",
    #     'slTriggerPx': stop_loss_price,
    # }
    # print('---------止损价 执行----------------------------------')

    # data = exchange.create_order(
    #     'BTC/USDT', 'limit', 'sell', property_val, closing_price, exchange_params)
    # print(data)
    # print(type(data))

    # print('---------止盈价 执行----------------------------------')

    # exchange_params = {
    #     'stopPrice': closing_price,
    #     'type': 'stopLimit',
    # }
    # data = exchange.create_order(
    #     'DOT/USDT', 'limit', 'sell', property_val, closing_price, exchange_params)
    # print(data)
    # print(type(data))


def testK_buy_close():
    # 平多
    data = exchange.create_limit_buy_order(
        'DOT/USDT', 1, 5, {"tdMode": "cross"})
    print(data)
    print(type(data))

    # closed_orders = exchange.fetchClosedOrders('BTC/USDT', limit=2)
    # print(closed_orders)

    # closed_orders = exchange.fetchMyTrades('ETH/USDT', limit=2)
    # print(closed_orders)


def testK_sell_open():
    # 做空开仓

    # data = exchange.createMarketSellOrder(
    #     'DOT/USDT', 1, {"tdMode": "cross", 'ccy': "USDT", })
    # print(data)
    # print(type(data))

    # 数据
    # {'info': {'clOrdId': 'e847386590ce4dBC58e8b0afb0fe70cc', 'ordId': '554437054223302656', 'sCode': '0', 'sMsg': 'Order placed', 'tag': 'e847386590ce4dBC'}, 'id': '554437054223302656', 'clientOrderId': 'e847386590ce4dBC58e8b0afb0fe70cc', 'timestamp': None, 'datetime': None, 'lastTradeTimestamp': None, 'symbol': 'DOT/USDT', 'type': 'market', 'timeInForce': None, 'postOnly': None, 'side': 'buy', 'price': None, 'stopPrice': None, 'triggerPrice': None, 'average': None, 'cost': None, 'amount': None, 'filled': None, 'remaining': None, 'status': None, 'fee': None, 'trades': [], 'reduceOnly': None, 'fees': []}

    # # 查询委托单
    # order_id = data['info']['ordId']
    order_id = '554516809819832320'
    data = exchange.fetchOrder(order_id, 'DOT/USDT')
    print(data['info'])
    # {'info': {'accFillSz': '0.190548', 'algoClOrdId': '', 'algoId': '', 'avgPx': '5.248', 'cTime': '1678441709955', 'cancelSource': '', 'cancelSourceReason': '', 'category': 'normal', 'ccy': 'USDT', 'clOrdId': 'e847386590ce4dBCeaddfd1494dc7080', 'fee': '-0.000190548', 'feeCcy': 'DOT', 'fillPx': '5.248', 'fillSz': '0.190548', 'fillTime': '1678441709957', 'instId': 'DOT-USDT', 'instType': 'MARGIN', 'lever': '10', 'ordId': '554359943143833600', 'ordType': 'market', 'pnl': '0', 'posSide': 'net', 'px': '', 'quickMgnType': '', 'rebate': '0', 'rebateCcy': 'USDT', 'reduceOnly': 'false', 'side': 'buy', 'slOrdPx': '', 'slTriggerPx': '', 'slTriggerPxType': '', 'source': '', 'state': 'filled', 'sz': '1', 'tag': 'e847386590ce4dBC', 'tdMode': 'cross', 'tgtCcy': '', 'tpOrdPx': '', 'tpTriggerPx': '', 'tpTriggerPxType': '', 'tradeId': '81184616', 'uTime': '1678441709960'}, 'id': '554359943143833600', 'clientOrderId': 'e847386590ce4dBCeaddfd1494dc7080', 'timestamp': 1678441709955, 'datetime': '2023-03-10T09:48:29.955Z', 'lastTradeTimestamp': 1678441709957, 'symbol': 'DOT/USDT', 'type': 'market', 'timeInForce': 'IOC', 'postOnly': None, 'side': 'buy', 'price': 5.248, 'stopPrice': None, 'triggerPrice': None, 'average': 5.248, 'cost': 0.999995904, 'amount': 1.0, 'filled': 0.190548, 'remaining': 0.809452, 'status': 'closed', 'fee': {'cost': 0.000190548, 'currency': 'DOT'}, 'trades': [], 'reduceOnly': False, 'fees': [{'cost': 0.000190548, 'currency': 'DOT'}]}

    open_price = data['info']['avgPx']

    print("开仓平均价", open_price)

    # 止盈价
    closing_price = float(open_price) * float((1 - 0.005))
    closing_price = common.roundVal(closing_price, open_price)
    print("止盈价", closing_price)

    # 止损价
    stop_loss_price = float(open_price) * float((1 + 0.01))
    stop_loss_price = common.roundVal(stop_loss_price, open_price)
    print("止损价", stop_loss_price)

    property_val = float(data['info']['accFillSz'])
    # 相同位数
    print("可平仓资产", property_val)

    # 止损价
    # 止盈价
    exchange_params = {
        'ccy': "USDT",
        'reduceOnly': True,
        'tdMode': "cross",
        'tpOrdPx': "-1",
        'tpTriggerPx': closing_price,
        'slOrdPx': "-1",
        'slTriggerPx': stop_loss_price,
    }
    print('---------止损价 执行----------------------------------')

    data = exchange.create_order(
        'DOT/USDT', 'limit', 'buy', property_val, closing_price, exchange_params)
    print(data)
    print(type(data))


def testK_sell_close():
    # 平多
    data = exchange.create_limit_buy_order(
        'DOT/USDT', 1, 5, {"tdMode": "cross"})
    print(data)
    print(type(data))

    # closed_orders = exchange.fetchClosedOrders('BTC/USDT', limit=2)
    # print(closed_orders)

    # closed_orders = exchange.fetchMyTrades('ETH/USDT', limit=2)
    # print(closed_orders)

if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'long':
        longRun()
    elif func == 'run':
        debug()
    elif func == 'test':
        testKdan()
    elif func == 't_get_trade':
        t_get_trade()
    elif func == 't_buy_open':
        testK_buy_open()
    elif func == 't_buy_close':
        testK_buy_close()
    elif func == 't_sell_open':
        testK_sell_open()
    elif func == 't_sell_cloe':
        testK_sell_close()
    else:
        print('error')
