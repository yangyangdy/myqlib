import backtrader as bt
import sys

# 自定义一个信号指标
class SignalDoubleSMA(bt.Indicator):
    lines = ('signal',)  # 定义一个元组 声明signal线，交易信号放在signal line上
    params = dict(
        short_period=5,
        long_period=20)
    def __init__(self):
        self.s_ma = bt.ind.SMA(period=self.p.short_period)
        self.l_ma = bt.ind.SMA(period=self.p.long_period)
        # 短期均线上穿长期均线，取值为1；反之，短期均线下穿长期均线，取值为-1
        self.lines.signal = bt.ind.CrossOver(self.s_ma, self.l_ma)

# 三均线策略
# 短，中，长三条线，短期>中期>长期，呈现多头排列时买入，短线下穿时平仓

class SignalTripleSMA(bt.Indicator):
    lines = ('signal',)  # 声明signal线，交易信号放在signal line上
    params = dict(
        short_period=5,
        median_period=20,
        long_period=60
    )

    def __init__(self):
        self.s_ma = bt.ind.SMA(period=self.p.short_period)
        self.m_ma = bt.ind.SMA(period=self.p.meidan_period)
        self.l_ma = bt.ind.SMA(period=self.p.long_period)

        # 短期均线在中期均线上方，且中期均线也在长期均线上方，三线多头排列，取值为1；反之，取值为0
        self.signal1 = bt.And(self.m_ma > self.l_ma, self.s_ma > self.m_ma)
        # 求上面self.signal1的环比量，可以判断得到第一次同时满足上述条件的时间，第一次满足条件为1，其余条件为0
        self.buy_signal = bt.If((self.signal1 - self.signal1(-1)) > 0, 1, 0)
        # 短期均线下穿长期均线时，取值为1；反之取值为0
        self.sell_signal = bt.ind.CrossDown(self.s_ma, self.m_ma)
        # 将买卖信号合并成一个信号
        self.lines.signal = bt.Sum(self.buy_signal, self.sell_signal*(-1))
