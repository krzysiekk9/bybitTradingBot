import pandas_ta as ta

def create_rma_indicator(df):
    df["rma33_low"] = ta.rma(df["low"], length=33)
    df["rma33_high"] = ta.rma(df["high"], length=33)
    df["rma144_low"] = ta.rma(df["low"], length=144)
    df["rma144_high"] = ta.rma(df["high"], length=144)

def create_macd_indicator(df):
    my_macd = ta.macd(df["close"])  #pd.DataFrame: macd, histogram, signal columns.
    df["MACD_12_26_9"] = my_macd["MACD_12_26_9"]
    df["MACDh_12_26_9"] = my_macd["MACDh_12_26_9"]
    df["MACDs_12_26_9"] = my_macd["MACDs_12_26_9"]


def create_bbands_indicator(df):
    my_bbands = ta.bbands(df["close"], length=14)
    df["BBL_14_2.0"] = my_bbands["BBL_14_2.0"] 
    df["BBU_14_2.0"] = my_bbands["BBU_14_2.0"]

def create_rsi_indicator(df):
    my_rsi = ta.rsi(df["close"], length=14)
    df["rsi"] = my_rsi