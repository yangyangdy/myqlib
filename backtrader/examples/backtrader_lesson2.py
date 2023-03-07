import backtrader as bt
import math

# 基本的策略派生类如下所示
class MyStrategy(bt.Strategy):
    def __init_(self):
        self.sma = bt.ind.MovingAverageSimple(self.data, period=20)

    def next(self):
        if self.sma > self.data.close:
            submitted_order = self.buy()
        elif self.sma < self.data.close:
            submitted_order = self.sell()

    def start(self):
        print('Backtesting is about to start')

    def stop(self):
        print('Backtesting is finished')

    def notify_order(self, order):
        print('An order new/changed/executed/canceled has been received')

