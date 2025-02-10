'''
pip install git+https://github.com/catalyst-team/catalyst@master --upgrade


cd /www/server/mdserver-web && python3 plugins/cryptocurrency_trade/ccxt/test/p1.py


cd /Users/midoks/Desktop/mwdev/server/mdserver-web &&  source bin/activate

python3 plugins/cryptocurrency_trade/ccxt/test/p1.py
'''

from datetime import datetime
import akshare as ak
import pandas as pd
import backtrader as bt


import sys
import os

sys.path.append(os.getcwd() + "/plugins/cryptocurrency_trade/ccxt/strategy")
import common


class BollStrategy(bt.Strategy):  # BOLL策略程序
    params = (("nk", 13),  # 求均值的天数
              ('printlog', False),)  # 打印log

    def __init__(self):  # 初始化
        self.data_close = self.datas[0].close  # 指定价格序列
        # 初始化交易指令、买卖价格和手续费
        self.order = None
        self.buy_price = None
        self.buy_comm = None
        # Boll指标计算
        self.top = bt.indicators.BollingerBands(
            self.datas[0], period=self.params.nk).top
        self.bot = bt.indicators.BollingerBands(
            self.datas[0], period=self.params.nk).bot
        # 添加移动均线指标
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.nk)

    def next(self):  # 买卖策略
        if self.order:  # 检查是否有指令等待执行
            return
        # 检查是否持仓
        """
        if not self.position:  # 没有持仓
            if self.data_close[0] > self.sma[0]:  # 执行买入条件判断：收盘价格上涨突破20日均线
                self.order = self.buy(size=100)  # 执行买入
        else:
            if self.data_close[0] < self.sma[0]:  # 执行卖出条件判断：收盘价格跌破20日均线
                self.order = self.sell(size=100)  # 执行卖出
        """
        if not self.position:  # 没有持仓
            if self.data_close[0] < self.bot[0]:  # 收盘价格跌破下轨
                self.log("BUY CREATE, %.2f" % self.data_close[0])
                self.order = self.buy()  # 执行买入
        else:
            if self.data_close[0] > self.top[0]:  # 收盘价格上涨突破上轨
                self.log("SELL CREATE, %.2f" % self.data_close[0])
                self.order = self.sell()  # 执行卖出

    def log(self, txt, dt=None, do_print=False):  # 日志函数
        if self.params.printlog or do_print:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):  # 记录交易执行情况
        # 如果order为submitted/accepted,返回空
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 指令为buy/sell,报告价格结果
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f"买入:\n价格:{order.executed.price},\
                成本:{order.executed.value},\
                手续费:{order.executed.comm}"
                )
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(
                    f"卖出:\n价格：{order.executed.price},\
                成本: {order.executed.value},\
                手续费{order.executed.comm}"
                )
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("交易失败")  # 指令取消/交易失败, 报告结果
        self.order = None

    def notify_trade(self, trade):  # 记录交易收益情况
        if not trade.isclosed:
            return
        self.log(f"策略收益：\n毛收益 {trade.pnl:.2f}, 净收益 {trade.pnlcomm:.2f}")

    def stop(self):  # 回测结束后输出结果
        self.log("(BOLL线： %2d日) 期末总资金 %.2f" %
                 (self.params.nk, self.broker.getvalue()), do_print=True)

code = "600036"  # 股票代码
start_cash = 1000000  # 初始自己为1000000
stake = 100  # 单次交易数量为1手
commfee = 0.0005  # 佣金为万5
sdate = '20210101'  # 回测时间段
edate = '20220930'
cerebro = bt.Cerebro()  # 创建回测系统实例
# 利用AKShare获取股票的前复权数据的前6列
# df_qfq = ak.stock_zh_a_hist(
#     symbol=code, adjust="qfq", start_date=sdate, end_date=edate).iloc[:, :6]
#              日期     开盘     收盘     最高     最低      成交量
# 0    2021-01-04  40.46  40.40  41.01  39.25  1549523
# 1    2021-01-05  39.99  39.41  40.03  38.67  1387177
# 2    2021-01-06  39.33  41.38  41.43  39.23  1200646
# 3    2021-01-07  41.52  43.13  43.20  41.49  1078322
# 4    2021-01-08  43.52  43.83  44.25  43.04  1299595
# ..          ...    ...    ...    ...    ...      ...
# 420  2022-09-26  34.02  33.95  34.52  33.84   525491
# 421  2022-09-27  33.89  33.90  34.05  33.44   475414
# 422  2022-09-28  33.79  33.67  34.00  33.42   487299
# 423  2022-09-29  33.99  33.15  34.32  33.00   617859
# 424  2022-09-30  33.26  33.65  33.95  33.12   539717

tag = 'btc'
symbol = tag.upper() + '/USDT'
df_qfq = common.getDataFromDb_DF('15m', tag.lower())
print(df_qfq)

# # 处理字段命名，以符合Backtrader的要求
# df_qfq.columns = ['date', 'open', 'close', 'high', 'low', 'volume', ]
# # 把date作为日期索引，以符合Backtrader的要求
# df_qfq.index = pd.to_datetime(df_qfq['date'])
# start_date = datetime.strptime(sdate, "%Y%m%d")  # 转换日期格式
# end_date = datetime.strptime(edate, "%Y%m%d")
start_date = datetime(2023, 4, 6)
end_date = datetime(2023, 4, 9)
data = bt.feeds.PandasData(dataname=df_qfq, fromdate=start_date,
                           todate=end_date)  # 规范化数据格式

cerebro.adddata(data)  # 加载数据
cerebro.addstrategy(BollStrategy, nk=13, printlog=True)  # 加载交易策略
cerebro.broker.setcash(start_cash)  # broker设置资金
cerebro.broker.setcommission(commission=commfee)  # broker手续费
cerebro.addsizer(bt.sizers.FixedSize, stake=stake)  # 设置买入数量
print("期初总资金: %.2f" % start_cash)
cerebro.run()  # 运行回测
end_value = cerebro.broker.getvalue()  # 获取回测结束后的总资金
print("期末总资金: %.2f" % end_value)
# cerebro.plot(style='candle')
