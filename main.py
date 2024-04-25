from pybit.unified_trading import HTTP
from datetime import datetime
import pandas as pd
import numpy as np

from threading import Timer
import time
import json
import string
import random

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
    category="inverse",
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

# for index, row in df.iterrows():
#         df['position'] = df.apply(lambda row: signal_point_break(row), axis=1)

# figure.draw_figure(df)

# print(df)

def check_for_currently_open_position():
    response = session.get_positions(
    category="inverse",
    symbol="BTCUSDT"
    )

    s1 = json.dumps(response['result']['list'][0])
    details = json.loads(s1)

    return details['symbol'], details['side'], details['size']


def set_SL_and_TP(side, rma144H, rma144L, open_price):
    if(side == "long"):
        if(open_price < rma144H):
            stop_loss = open_price - 200
            take_profit = (open_price - stop_loss) * 2 + open_price
            return stop_loss, take_profit
        if(open_price >= rma144H):
            stop_loss = rma144H - 30
            take_profit = (open_price - stop_loss) * 2 + open_price
            return stop_loss, take_profit
    if(side == "short"):
        if(open_price > rma144L):
            stop_loss = open_price + 200
            take_profit = open_price - ((stop_loss - open_price) * 2)
            return stop_loss, take_profit
        if(open_price <= rma144L):
            stop_loss = round(rma144L + 30, 1)
            take_profit = round((open_price - ((stop_loss - open_price) * 2)), 1)
            return stop_loss, take_profit
        
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def check_to_open_new_position(row):
    signal = row.signal
    rma144H = row.rma144_high
    rma144L = row.rma144_low
    open_price = row.close

    symbol, side, size = check_for_currently_open_position()

    if(float(size) == 0): #no open position and can open a new one
        if(signal==1): #open long position
            print('Opening logn position')
            stop_loss, take_profit = set_SL_and_TP("long", rma144H, rma144L, open_price)
            session.place_order(
                category="inverse",
                symbol="BTCUSD",
                side="Buy",
                orderType="Limit",
                qty="100",
                price=str(round(open_price, 1)),
                takeProfit=str(take_profit),
                stopLoss=str(stop_loss),
                timeInForce="PostOnly",
                orderLinkId=f"spot-test-postonly-id-{id_generator()}",
                isLeverage=0,
                orderFilter="Order",
            )
        if(signal==2): #open short position
            print('Opening short position')
            stop_loss, take_profit = set_SL_and_TP("short", rma144H, rma144L, open_price)
            session.place_order(
                category="inverse",
                symbol="BTCUSD",
                side="Sell",
                orderType="Limit",
                qty="100",
                price=str(round(open_price, 1)),
                takeProfit=str(take_profit),
                stopLoss=str(stop_loss),
                timeInForce="PostOnly",
                orderLinkId=f"spot-test-postonly-id-{id_generator()}",
                isLeverage=0,
                orderFilter="Order",
            )
        else:
            print('Opening short position')
            stop_loss, take_profit = set_SL_and_TP("short", rma144H, rma144L, open_price)
            session.place_order(
                category="inverse",
                symbol="BTCUSD",
                side="Sell",
                orderType="Limit",
                qty="5",
                price=str(round(open_price, 1)),
                takeProfit=str(take_profit),
                stopLoss=str(stop_loss),
                timeInForce="PostOnly",
                orderLinkId=f"spot-test-postonly-id-{id_generator()}",
                isLeverage=0,
                orderFilter="Order",
            )


def update_data(): #update data every minute

    response = session.get_kline( # after specified interval get newest candle data
        category="inverse",
        symbol=config.SYMBOL,
        interval=config.INTERVAL,
        start=config.TIME_UPDATE,
        end=config.TIME_END,
        limit=1
    )

    updated_data = response['result']['list'][0]

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
    print('dupa dupa')
    
    check_to_open_new_position(df.iloc[-1])
    return df



t = Timer(5.0, update_data)
t.start()


