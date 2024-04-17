from pybit.unified_trading import HTTP
from datetime import datetime
import pandas as pd
import pandas_ta as ta

import config

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

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

# df["sma_low"] = df["close"].rolling(window=33).mean()
# df["sma_high"] = df["close"].rolling(window=144).mean()

df["rma33_low"] = ta.rma(df["low"], length=33)
df["rma33_high"] = ta.rma(df["high"], length=33)
df["rma144_low"] = ta.rma(df["low"], length=144)
df["rma144_high"] = ta.rma(df["high"], length=144)

my_macd = ta.macd(df["close"])  #pd.DataFrame: macd, histogram, signal columns.
my_bbands = ta.bbands(df["close"], length=14)

fig = make_subplots(rows=2, cols=1,
                    row_heights=[0.85, 0.15], 
                    shared_xaxes=True, 
                    subplot_titles=("BTCUSDT","MACD"),
                    vertical_spacing = 0.05)

fig.add_trace(go.Candlestick(x=df.index,
                             open=df["open"], 
                             high=df["high"],
                             low=df["low"], 
                             close=df["close"]),
                             row=1, col=1)

fig.add_trace(go.Scatter(x=df.index, 
                         y=df["rma33_low"], 
                         line=dict(color='#00bcd4',width=1), 
                         name='RMA33L'))
fig.add_trace(go.Scatter(x=df.index, 
                         y=df["rma33_high"], 
                         line=dict(color='#00bcd4',width=1),
                         name='RMA33H'))                
fig.add_trace(go.Scatter(x=df.index, 
                         y=df["rma144_low"], 
                         line=dict(color='#ff5252',width=1),
                         name='RMA144L'))                
fig.add_trace(go.Scatter(x=df.index, 
                         y=df["rma144_high"], 
                         line=dict(color='#ff5252',width=1),
                         name='RMA144H'))                



fig.add_trace(go.Scatter(x=df.index, y=my_bbands["BBL_14_2.0"], name='BBL'))
fig.add_trace(go.Scatter(x=df.index, y=my_bbands["BBU_14_2.0"], name='BBU'))


fig.add_trace(go.Scatter(x=df.index, y=my_macd["MACD_12_26_9"],
                        marker_color="#303030",
                        name='MACD'), row=2, col=1)
fig.add_trace(go.Scatter(x=df.index, y=my_macd["MACDs_12_26_9"], 
                     marker_color="#2205b3",
                     name='MACDS'),row=2, col=1)
fig.add_trace(go.Bar(x=df.index, y=my_macd["MACDh_12_26_9"], 
                     marker_color="#cfcfcf",
                     name='MACDH'),row=2, col=1)

fig.update_layout(xaxis_rangeslider_visible=False)
fig.update_layout(yaxis_title="USDT")


fig.show()

#FIXME fix indicators on x axis
#TODO add possibility to test strategy on past candles
#TODO add opening positions and closing them