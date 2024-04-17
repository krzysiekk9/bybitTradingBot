import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas_ta as ta

def create_rma_indicator(df):
    df["rma33_low"] = ta.rma(df["low"], length=33)
    df["rma33_high"] = ta.rma(df["high"], length=33)
    df["rma144_low"] = ta.rma(df["low"], length=144)
    df["rma144_high"] = ta.rma(df["high"], length=144)

def create_macd_indicator(df):
    return ta.macd(df["close"])  #pd.DataFrame: macd, histogram, signal columns.

def create_bbands_indicator(df):
    return ta.bbands(df["close"], length=14)

def draw_figure(df):

    create_rma_indicator(df)
    my_macd = create_macd_indicator(df)
    my_bbands = create_bbands_indicator(df)

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