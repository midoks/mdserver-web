# plugins_cryptocurrency_trade

- https://docs.ccxt.com/en/latest/install.html#python-proxies

数字货币量化交易插件

```
cd /www/server/mdserver-web &&  python3 plugins/cryptocurrency_trade/ccxt/okex/strategy/st_demo.py

python3 plugins/cryptocurrency_trade/ccxt/okex/strategy/st_demo.py

miniconda3



```

# 免费TV策略
https://cn.tradingview.com/scripts/?script_type=strategies


### tradingview pine 指标
```
// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © TenCloud

//@version=5
indicator("第一个指标",shorttitle = "开心吧")

ema10 = ta.ema(close, 25)
ema100 = ta.ema(close, 100)
l1=plot(ema10, color=color.red,title = "ema10")
l2=plot(ema100,color = color.green, title = "ema100")


buy = ta.crossover(ema10,ema100)
sell = ta.crossunder(ema10,ema100)

plotchar(buy, text = "buy", color=color.green)
plotchar(sell, text="sell", color=color.red)

l_color = ema10>ema100 ? color.green:color.red

fill(l1,l2,color=color.new(l_color,70))

```

### tradingview pine 策略
```
// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © TenCloud

//@version=5
strategy("第一个指标",shorttitle = "开心吧", overlay = true, initial_capital = 1000)

ema10 = ta.ema(close, 25)
ema100 = ta.ema(close, 100)
l1=plot(ema10, color=color.red,title = "ema10")
l2=plot(ema100,color = color.green, title = "ema100")


buy = ta.crossover(ema10,ema100)
sell = ta.crossunder(ema10,ema100)

if buy
    strategy.entry("long1", strategy.long,1)

if sell
    strategy.close("long1", qty_percent = 100,comment = "平仓多单")
// plotchar(buy, text = "buy", color=color.green)
// plotchar(sell, text="sell", color=color.red)

// l_color = ema10>ema100 ? color.green:color.red

// fill(l1,l2,color=color.new(l_color,70))


```