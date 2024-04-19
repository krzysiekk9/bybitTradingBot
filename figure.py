import plotly.graph_objects as go
from plotly.subplots import make_subplots

def draw_figure(df):

    fig = make_subplots(rows=3, cols=1,
                        row_heights=[0.8, 0.1, 0.1], 
                        shared_xaxes=True, 
                        subplot_titles=("BTCUSDT","MACD","RSI"),
                        vertical_spacing = 0.02)

    #subplot 1
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

    fig.add_trace(go.Scatter(x=df.index, y=df.pointbreak,
                            mode="markers", 
                            marker=dict(size=15, color="#7b30d1", symbol='triangle-up'),
                            name="Signal"),
                            row=1, col=1)              

    # fig.add_trace(go.Scatter(x=df.index, y=df["BBL_14_2.0"], name='BBL', marker_color="#f4e755",))
    # fig.add_trace(go.Scatter(x=df.index, y=df["BBU_14_2.0"], name='BBU', marker_color="#f4e755",))

    #subplot 2
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD_12_26_9"],
                            marker_color="#2962FF",
                            line_width=1,
                            name='MACD'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["MACDs_12_26_9"], 
                        marker_color="#FF6D00",
                        line_width=1,
                        name='MACDS'),row=2, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df["MACDh_12_26_9"], 
                        marker_color="#cfcfcf",
                        name='MACDH'),row=2, col=1)
    
    #subplot 3
    fig.add_trace(go.Scatter(x=df.index, y=df["rsi"],
                             marker_color="#7E57C2",
                             name='RSI'
                             ), row=3, col=1)
    
    fig.add_hline(y=60, line_width=1, line_dash="dash", line_color="black", opacity=0.5, row=3, col=1)
    fig.add_hline(y=40, line_width=1, line_dash="dash", line_color="black", opacity=0.5, row=3, col=1)

    fig.update_layout(xaxis_rangeslider_visible=False)
    fig.update_layout(yaxis_title="USDT")


    fig.show()