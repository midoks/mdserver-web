# coding:utf-8

import pandas as pd

import matplotlib.pyplot as plt


from catalyst import run_algorithm
from catalyst.api import order, record, symbol

'''
cd /Users/midoks/Desktop/mwdev/server/mdserver-web &&  source bin/activate


cd /www/server/mdserver-web &&  source bin/activate && source activate catalys

cd /Users/midoks/Desktop/mwdev/server/mdserver-web && python3 plugins/cryptocurrency_trade/ccxt/test/p_test.py
catalyst ingest-exchange -x binance -i btc_usdt -f minute

cd /www/server/mdserver-web && python3 plugins/cryptocurrency_trade/ccxt/test/p_test.py
'''


def initialize(context):
    # 初始化
    context.asset = symbol('btc_usdt')


def handle_data(context, data):
    # 循环策略
    order(context.asset, 1)
    record(btc=data.current(context.asset, 'price'))


def analyze(context, perf):

    print(perf.portfolio_value)

    ax1 = plt.subplot(211)
    perf.portfolio_value.plot(ax=ax1)

    ax1.set_ylabel('portfolio value')

    ax2 = plt.subplot(212, sharex=ax1)
    perf.btc.plot(ax=ax2)
    ax2.set_ylabel('bitcoin value')
    plt.show()


if __name__ == "__main__":
    run_algorithm(
        capital_base=10000,
        data_frequency='daily',
        initialize=initialize,
        handle_data=handle_data,
        analyze=analyze,
        exchange_name='binance',
        quote_currenty='usdt',
        start=pd.to_datetime("2018-01-01", utc=True),
        end=pd.to_datetime("2018-10-01", utc=True),
    )
