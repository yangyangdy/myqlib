import os
import backtrader as bt
from datetime import datetime
import pandas as pd
import tushare as ts

# data_path = './data/'
# if not os.path.exists(data_path):
#     os.makedirs(data_path)
# mytoken = 'your_token'

# Create a subclass of Strategy to define the indicators and logic
# bt.Strategy是用户策略的基类，开发者需要重写一个继承bt.Strategy的子类
# 有两个重要的函数需要override  __init__ 和 next
# __init__()是在回测前对个性化数据进行计算
# next中存放针对每个Bar的交易逻辑指令，在next()中对情况进行判断并作出买卖指定。
class SmaCross(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = dict(
        pfast=10,  # period for the fast moving average
        pslow=30   # period for the slow moving average
    )
    def __init__(self):
        super().__init__()
        sma1 = bt.ind.SMA(period=self.p.pfast)  # fast moving average
        sma2 = bt.ind.SMA(period=self.p.pslow)  # slow moving average
        self.crossover = bt.ind.CrossOver(sma1, sma2)  # crossover signal
    def next(self):
        if not self.position:  # not in the market
            if self.crossover > 0:  # if fast crosses slow to the upside
                self.order_target_size(target=1)  # enter long
                # self.buy()
        elif self.crossover < 0:  # in the market & cross to the downside
            self.order_target_size(target=0)  # close long position
            # self.close()

class Strategy_runner:
    def __init__(self, strategy, ts_code, start_date, end_date, data_path, csv_name):
        self.ts_code = ts_code
        self.start_date = start_date
        self.end_date = end_date
        # convert to datetime
        self.start_datetime = datetime.strptime(start_date, '%Y%m%d')
        self.end_datetime = datetime.strptime(end_date, '%Y%m%d')
        # if pro:
        #     csv_name = f'pro_day_{str(ts_code)}-{str(start_date)}-{str(end_date)}.csv'
        # else:
        #     csv_name = f'day_{str(ts_code)}-{str(start_date)}-{str(end_date)}.csv'
        csv_path = os.path.join(data_path, csv_name)
        if os.path.exists(csv_path):
            self.df = pd.read_csv(csv_path, index_col=0)
        # else:
        #     if pro:
        #         ts.set_token(mytoken)
        #         self.pro = ts.pro_api()
        #         self.df = self.pro.daily(ts_code=self.ts_code, start_date=self.start_date, end_date=self.end_date)
        #         if not self.df.empty:
        #             self.df.to_csv(csv_path, index=False)
        #     else:
        #         self.df = ts.get_hist_data(self.ts_code, str(self.start_datetime), str(self.end_datetime))
        #         if not self.df.empty:
        #             self.df.to_csv(csv_path, index=True)

        self.df_bt = self.preprocess(self.df, True)
        print(self.df_bt)
        self.strategy = strategy
        self.cerebro = bt.Cerebro()


    def preprocess(self, df, pro=True):
        if pro:
            features = ['open', 'high', 'low', 'close', 'vol', 'trade_date']
            # convert_datetime = lambda x:datetime.strptime(x,'%Y%m%d')
            convert_datetime = lambda x: pd.to_datetime(str(x))
            df['trade_date'] = df['trade_date'].apply(convert_datetime)
            print(df)
            bt_col_dict = {'vol': 'volume', 'trade_date': 'datetime'}
            df = df.rename(columns=bt_col_dict)
            df = df.set_index('datetime')
            # df.index = pd.DatetimeIndex(df.index)
        else:
            features = ['open', 'high', 'low', 'close', 'volume']
            df = df[features]
            df['openinterest'] = 0
            df.index = pd.DatetimeIndex(df.index)

        df = df[::-1]  # 将数据反转
        return df

    def run(self):
        '''
        交易场景的设置要尽可能地模拟真实场景，常见的条件
        初始资金，交易税费，滑点，期货保证金比率等
        对成交量做限制，对涨跌幅做限制，对订单的生成和执行时机做限制
        在backtrader中可以通过broker来管理
        推荐下面的使用方式
        def next(self):
        print('当前可用资金', self.broker.getcash())
        print('当前总资产', self.broker.getvalue())
        print('当前持仓量', self.broker.getposition(self.data).size)
        print('当前持仓成本', self.broker.getposition(self.data).price)
        # 也可以直接获取持仓
        print('当前持仓量', self.getposition(self.data).size)
        print('当前持仓成本', self.getposition(self.data).price)

        01 滑点
        一般滑点在所难免，由于网络延时、市场波动等原因。
        滑点分为百分比、固定两种。以高于+p的价格买，以低于-P的价格卖出。
        若二者均设置，则百分比优先级高。
        cerebro.broker.set_slippage_perc(0.0001)
        cerebro.broker.set_slippage_fixed(0.03)

        02 交易费用
        交易费用不可忽视，尤其是在交易频率比较高的策略中。
        bt中简单配置交易费用很容易，但如果要更真实的模拟市场，则需要了解一些细节。
        比如交易费率为“万分之三”，买卖都收，直接setcommission即可。
        cerebro.broker.setcommission(0.0003)
        但A股实际上还有一个单笔不低于5元，且卖出还有印花税。
        这就需要继承bt.CommInfoBase，然后自己写计算逻辑。
        class MyStockCommissionScheme(bt.CommInfoBase):
            # 1.佣金按照百分比。    2.每一笔交易有一个最低值，比如5块，当然有些券商可能会免5.
            # 3.卖出股票还需要收印花税。    4.可能有的平台还需要收平台费。
            params = (
                ('stampduty', 0.005),  # 印花税率
                ('commission', 0.005),  # 佣金率
                ('stocklike', True),#股票类资产，不考虑保证金
                ('commtype', bt.CommInfoBase.COMM_PERC),#按百分比
                ('minCommission', 5),#最小佣金
                ('platFee', 0),#平台费用
            )

            def _getcommission(self, size, price, pseudoexec):
                # size>0，买入操作。        size<0，卖出操作。
                if size > 0:  # 买入，不考虑印花税，需要考虑最低收费
                    return max(size * price * self.p.commission,self.p.minCommission)+platFee
                elif size < 0:  # 卖出，考虑印花税。
                    return max(abs(size) * price * self.p.commission,self.p.minCommission)+abs(size) * price * self.p.stampduty+platFee
                else:
                    return 0  # 防止特殊情况下size为0.
        cerebro.broker.setcommission(0.0003)
        cerebro.broker.addcommissioninfo(MyStockCommissionScheme())

        03 交易订单类型
        回测中使用比较多的还是市价单和限价单。
        bt支持市值，限价，止损，止损限价，止损追踪，止损追踪限价。
        默认是市价单，就是使用下一个Bar的open来交易。
        self.buy(exectype=bt.Order.Market)

        04 交易函数
        策略的核心就是依照计算好的规则，向broker发布交易指令。
        指令有常规的买或卖，或有按目标下单。
        常规买卖就是 buy, sell, close。买、卖和平仓。
        而目标下单函数会根据交易目标自动确定买卖方向。
        1， order_target_size，成交后到多少份
        2，order_target_value,成交后仓位到多少
        3， order_target_percent，成交后仓位占比
        # 按目标数量下单
        self.order = self.order_target_size(target=size)
        # 按目标金额下单
        self.order = self.order_target_value(target=value)
        # 按目标百分比下单
        self.order = self.order_target_percent(target=percent)

        ————————————————
        版权声明：本文为CSDN博主「AI量化投资实验室」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
        原文链接：https://blog.csdn.net/weixin_38175458/article/details/127294479
        Returns
        -------

        '''
        data = bt.feeds.PandasData(dataname=self.df_bt,
                                   fromdate=self.start_datetime,
                                   todate=self.end_datetime)
        self.cerebro.adddata(data)  # Add the data feed
        self.cerebro.addstrategy(self.strategy)  # Add the trading strategy
        self.cerebro.broker.setcash(100000.0)
        # self.cerebro.addsizer(bt.sizers.FixedSize, stake=10)
        # self.cerebro.broker.setcommission(commission=0.0)
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DW')
        self.results = self.cerebro.run()
        strat = self.results[0]
        print('Final Portfolio Value: %.2f' % self.cerebro.broker.getvalue())
        print('SR:', strat.analyzers.SharpeRatio.get_analysis())
        print('DW:', strat.analyzers.DW.get_analysis())
        return self.results

    def plot(self, iplot=False):
        self.cerebro.plot(iplot=iplot)

# stock_list = ['002475.SZ', '601688.SH', '601318.SH']
dataPath = '/Users/didi/quant_stock/data/'
csvName = '601318.SH.csv'
tsCode = '601318.SH'
startDate = '20180101'
endDate = '20230101'
strategy_runner = Strategy_runner(strategy=SmaCross, ts_code=tsCode, start_date=startDate, end_date=endDate, data_path=dataPath, csv_name=csvName)
results = strategy_runner.run()
strategy_runner.plot()
