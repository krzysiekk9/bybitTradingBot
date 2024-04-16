from pybit.unified_trading import HTTP
from datetime import datetime
import pandas as pd
import pandas_ta as ta

import config

import plotly.graph_objects as go
import plotly.express as px

session = HTTP(testnet=True)

# print(session.get_server_time()) #check the connection
print(config.TIME_END)
print("------------")
print(config.TIME_START)

response = session.get_kline(
    category="inverse",
    symbol=config.SYMBOL,
    interval=config.INTERVAL,
    # start=1670601600000,
    # end=1670608800000,
    start=config.TIME_START,
    end=config.TIME_END,
    # limit=1000
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
    data_dict["close"].append(i[4])

df = pd.DataFrame.from_dict(data_dict)


df["sma_low"] = df["close"].rolling(window=33).mean()
df["sma_high"] = df["close"].rolling(window=144).mean()

df["new"] = ta.sma(df["close"],30)

print(df)
# print('4'+df[4])
# print(response["result"]["list"])

fig = go.Figure(data=[go.Candlestick(x=df["date"],
                open=df["open"], high=df["high"],
                low=df["low"], close=df["close"])
                     ])

result = {"time":df["date"], "value":df["sma_low"]}
print(result)
fig.add_trace(go.Scatter(x=df['date'], y=df["new"])) #, line=dict(color="#f2f2f2")
# fig.add_trace(go.Scatter(x=df['date'], y=df["sma_high"]))
# fig.add_trace(px.scatter(df, x=['date'], y='sma_low'))
# fig.add_trace(go.Scatter(x=result["time"], y=result["value"]))


fig.update_layout(xaxis_rangeslider_visible=False)
fig.update_layout(yaxis_title="USDT", xaxis_title="Date")


fig.show()

#TODO add 2 moving averages depending on a time frame
#TODO add RSI or smth else
#TODO add possibility to test strategy on past candles
#TODO add opening positions and closing them