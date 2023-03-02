

'''
本教程用于介绍指标
SMA, EMA, MACD, KDJ, RSI, BOLL等
这些指标都封装在backtrader.indicators包中

使用方式
indicators指标可以在两个地方使用，一个是在策略中使用， 一个是在其他指标中使用
backtrader中使用内置需要完成下面两个步骤：
    1 在策略的__init__方法中实例化对应的指标
    2 在next方法中使用或检查对应的指标值或其衍生值
'''

# SMA简单移动平均指标的使用示例
# 需要说明的是：
# __init__方法中声明的任何指标都会在next方法调用之前进行计算
#
# 在__init__方法中针对lines对象的任何操作都会生成其他line对象(python操作符重载overriding)， 而在next方法会生成常规的python类型，如floats或bools
#
# __init__方法运算速度更快，同时可以使得next方法的逻辑更简单
#
# __init__方法不支持部分python操作符，需要使用bt内置函数来处理，如bt.And, bt.Or, bt.All, bt.Any。除了这些，backtrader还提供了bt.Cmp, bt.If, bt.Max, bt.Min, bt.Sum, bt.DivByZero等函数

import backtrader as bt
class MyStrategyExample(bt.Strategy):
    params = (('period', 20),)

    def __init__(self):
        self.sma = bt.indicators.SMA(self.data, period=self.period)
        ...

    def next(self):
        if self.sma[0] > self.data.close[0]:
            self.buy()
