from pybit.unified_trading import HTTP
from datetime import datetime
import pandas as pd
import numpy as np

from threading import Timer
import time

import config
import figure
import indicators
import wallet

session = HTTP(
    testnet=True,
    api_key=config.API,
    api_secret=config.SECRET,
)

account_wallet = wallet.create_wallet(session)

print(account_wallet)

response = session.get_kline(
    category="spot",
    symbol=config.SYMBOL,
    interval=config.INTERVAL,
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

def from_data_to_dictionary(data_dict, data):
    for i in reversed(data):
        start_time = datetime.fromtimestamp(int(i[0])/1000)
        data_dict["date"].append(start_time)
        data_dict["open"].append(float(i[1]))
        data_dict["high"].append(float(i[2]))
        data_dict["low"].append(float(i[3]))
        data_dict["close"].append(float(i[4]))

from_data_to_dictionary(data_dict, response['result']['list'])


df = pd.DataFrame.from_dict(data_dict)
# print(df)

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
    if(rma33L_0>=rma144L_0 and rma33H_0 >= rma144L_0):
        if(macd_0 >= macds_0 and (macd_1 <= macds_1 or macd_2 <= macds_2) and rsi_0 <= 55):
            return 1
    #down trend
    if(rma33L_0<=rma144L_0 and rma33H_0 <= rma144H_0 and rma33H_0 < rma144L_0 and current_close <= rma144L_0):
        if(macd_0 <= macds_0 and (macd_1 >= macds_1 or macd_2 >= macds_2) and rsi_0>=50):
            return 2
    else:
        return 0

def create_signal_table():
    signal = []
    signal.append(0)
    signal.append(0)

    for i in range(2, 1000):
        data_range = df[i-2:i+1]
        signal.append(signal_generator(data_range))

    df["signal"] = signal

create_signal_table()

def signal_point_break(x):
    if(x.signal==1):
        return x.close
    if(x.signal==2):
        return x.close
    if(x.signal==0):
        return np.nan

for index, row in df.iterrows():
        df['position'] = df.apply(lambda row: signal_point_break(row), axis=1)

figure.draw_figure(df)

# print(df)

def check_trade_signal(signal):
    if(signal==1):
        print('returning one')
        session.place_order(
            category="spot",
            symbol="BTCUSDC",
            side="Buy",
            orderType="Market",
            qty="0.005",
            timeInForce="PostOnly",
            orderLinkId="spot-test-postonly",
            isLeverage=0,
            orderFilter="Order",
        )
        
    elif(df.signal.iloc[-1]==2):
        print(df.signal.iloc[-1])
        print('returning two')
        session.place_order(
            category="spot",
            symbol="BTCUSDC",
            side="Sell",
            orderType="Market",
            qty="0.005",
            timeInForce="PostOnly",
            orderLinkId="spot-test-postonly",
            isLeverage=0,
            orderFilter="Order",
        )
    else:
        print('nothing')
        # pass

def update_data(): #update data every minute
    # response = client.ui_klines("BTCUSDT", f"{config.INTERVAL}m", limit=1)

    response = session.get_kline(
        category="spot",
        symbol=config.SYMBOL,
        interval=config.INTERVAL,
        start=config.TIME_UPDATE,
        end=config.TIME_END,
        limit=1
    )

    updated_data = response['result']['list'][0]
    print(updated_data)

    new_dict = {
    "date" : datetime.fromtimestamp(int(updated_data[0])/1000),
    "open": float(updated_data[1]),
    "high": float(updated_data[2]),
    "low": float(updated_data[3]),
    "close": float(updated_data[4])
    }

    df.loc[len(df.index)] = new_dict  #add new data to df in a new row

    #update indicators
    indicators.create_rma_indicator(df)
    indicators.create_macd_indicator(df)
    indicators.create_bbands_indicator(df)
    indicators.create_rsi_indicator(df)

    #check for signal
    df.loc[len(df.index) - 1,'signal'] = signal_generator(df.tail(3))

    #check for break point
    df.loc[len(df.index) - 1,'position'] = signal_point_break(df.iloc[-1])
    print(df)
    #TODO add checking if in position and if not and signal right buy
    check_trade_signal()
    #TODO add conditions to close position

t = Timer(1.0, update_data)
t.start()





# def

# client.order(**params)






#TODO add opening and closing position with SL position
#TODO add condition of closing position TP and SL
#TODO add possibility to test strategy on past candles stop loss
#TODO add opening positions and closing them
