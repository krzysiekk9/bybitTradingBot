from pybit.unified_trading import HTTP
from datetime import datetime
import pandas as pd
import numpy as np

import config
import figure
import indicators

session = HTTP(testnet=True)

# print(session.get_server_time()) #check the connection

response = session.get_kline(
    category="inverse",
    symbol=config.SYMBOL,
    interval=config.INTERVAL,
    # start=1670601600000,
    # end=1670608800000,
    start=config.TIME_START,
    end=config.TIME_END,
    limit=1000
)
data_dict = {
    "date" : [],
    "open": [],
    "high": [],
    "low": [],
    "close": []
}

for i in response["result"]["list"]:
    start_time = datetime.fromtimestamp(int(i[0])/1000)
    data_dict["date"].append(start_time)
    data_dict["open"].append(i[1])
    data_dict["high"].append(i[2])
    data_dict["low"].append(i[3])
    data_dict["close"].append(float(i[4]))

df = pd.DataFrame.from_dict(data_dict)

indicators.create_rma_indicator(df)
indicators.create_macd_indicator(df)
indicators.create_bbands_indicator(df)
indicators.create_rsi_indicator(df)



def signal_generator(data_range):
    rma33L_2 = data_range.rma33_low.iloc[-3]  #2 previous one
    rma33L_1 = data_range.rma33_low.iloc[-2]  # last one
    rma33L_0 = data_range.rma33_low.iloc[-1]  # present

    rma33H_2 = data_range.rma33_high.iloc[-3]  #2 previous one
    rma33H_1 = data_range.rma33_high.iloc[-2]  # last one
    rma33H_0 = data_range.rma33_high.iloc[-1]  # present

    rma144L_2 = data_range.rma144_low.iloc[-3]  #2 previous one
    rma144L_1 = data_range.rma144_low.iloc[-2]  # last one
    rma144L_0 = data_range.rma144_low.iloc[-1]  # present

    rma144H_2 = data_range.rma144_high.iloc[-3]  #2 previous one
    rma144H_1 = data_range.rma144_high.iloc[-2]  # last one
    rma144H_0 = data_range.rma144_high.iloc[-1]  # present

    macd_2 = data_range["MACD_12_26_9"].iloc[-3] #2 previous one
    macd_1 = data_range["MACD_12_26_9"].iloc[-2] # last one
    macd_0 = data_range["MACD_12_26_9"].iloc[-1] # present

    macds_2 = data_range["MACDs_12_26_9"].iloc[-3] #2 previous one
    macds_1 = data_range["MACDs_12_26_9"].iloc[-2] # last one
    macds_0 = data_range["MACDs_12_26_9"].iloc[-1] # present

    rsi_0 = data_range["rsi"].iloc[-1]

    current_close = data_range["close"].iloc[-1]

    #up trend
    # if(rma33L_0>=rma144L_0 and rma33H_0 >= rma144H_0
    #    and (rma33H_1<rma144H_1 or rma33L_2<rma144L_2)): #
    #     if(macd_0>macds_0):
    #         return 1
    
    if(rma33L_0>=rma144L_0 and rma33H_0 >= rma144L_0):
        if(macd_0 >= macds_0 and (macd_1 <= macds_1 or macd_2 <= macds_2) and rsi_0 <= 55):
            return 1
    #down trend
    if(rma33L_0<=rma144L_0 and rma33H_0 <= rma144H_0 and rma33H_0 < rma144L_0 and current_close <= rma144L_0):
        if(macd_0 <= macds_0 and (macd_1 >= macds_1 or macd_2 >= macds_2) and rsi_0>=50):
            return 2
    else:
        return 0

signal = []
signal.append(0)
signal.append(0)
buy_signal = []
buy_signal.append(0)
buy_signal.append(0)

sell_signal = []
sell_signal.append(0)
sell_signal.append(0)

for i in range(2, 1000):
    data_range = df[i-2:i+1]
    signal.append(signal_generator(data_range))

df["signal"] = signal

def pointbreak(x):
    if(x.signal==1):
        return x.close
    if(x.signal==2):
        return x.close
    else:
        return np.nan

for index, row in df.iterrows():
    df['pointbreak'] = df.apply(lambda row: pointbreak(row), axis=1)

print(signal)

print(df)

figure.draw_figure(df)

#types of signals
# 0 - down trend
# 1 - up trend
#FIXME fix xaxis
#TODO finish signal generator
#TODO add possibility to test strategy on past candles
#TODO add opening positions and closing them

# generate signal 
# signal trend -> check macd -> check bbands -> buy signal -> if in current candle open position 