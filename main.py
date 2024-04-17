from pybit.unified_trading import HTTP
from datetime import datetime
import pandas as pd
import pandas_ta as ta

import config
import figure

import plotly.graph_objects as go
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

figure.draw_figure(df)


#TODO add possibility to test strategy on past candles
#TODO add opening positions and closing them