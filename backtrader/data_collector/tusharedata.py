import os
import tushare as ts

data_path = '/Users/didi/quant_stock/data/'
startTime = '2000-01-01'
endTime = '2023-03-01'

# 002475.SZ lixun
# 601688.SH	huatai
# 601318.SH	pingan
stock_list = ['002475.SZ', '601688.SH', '601318.SH']

# 初始化pro接口
pro = ts.pro_api('')

# 拉取数据
for stock_code in stock_list:
    df = pro.daily(**{
        "ts_code": stock_code,
        "trade_date": "",
        "start_date": startTime,
        "end_date": endTime,
        "offset": "",
        "limit": ""
    }, fields=[
        "ts_code",
        "trade_date",
        "open",
        "high",
        "low",
        "close",
        "pre_close",
        "change",
        "pct_chg",
        "vol",
        "amount"
    ])
    file_path = data_path+stock_code
    if os.path.exists(file_path):
        df.to_csv(file_path+, na_rep='NA', header=0)  #不保存列名
    else:
        df.to_csv(file_path, na_rep='NA', header=1)  #保存列名

print("done")