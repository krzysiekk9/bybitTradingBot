# Trading Bot on Bybit exchange

This app is made using only python. 

For ploting chart I used plotly library, for managing data I used pandas, for indicators I used pandas_ta libarary.

---

## How does it wokr?

The app connect to the crypo exchange Bybit and gets user wallet (assets) information as well as chart data based on specified interval (I used 5 minutes interval).

After reciving, data is cleand and prepared (putted into pandas dataframe), afer that the indicators are calculated. When it's compleated each row is checked for position entry signal. If the given criteria are fulfilled appropriate flag is issued:

1 - up trend,

2 - down trend.

After that operation, each row is checked for a signal and if there is one the closed price of a candle is assigned. Next the chart is displayed with calculated signal break points.

Then, after a specified period of time, the data is updated with the latest market data. The application then checks whether the account is currently in a position, and if not, if a signal to open a position has occurred, the position is opened with a calculated stop loss and take profit.

---

### Displayed candlestick chart and indicators

![Screenshot 2024-04-25 101946](https://github.com/krzysiekk9/bybitTradingBot/assets/107801980/1f178b74-dbad-45ff-834a-e74cb6cb89a6)

### Displayed wallet with user assets

![Screenshot 2024-04-25 124331](https://github.com/krzysiekk9/bybitTradingBot/assets/107801980/cbab7ed0-390a-4d7b-ac69-b213e25f59fe)

### Displayed dataframe

![Screenshot 2024-04-25 124351](https://github.com/krzysiekk9/bybitTradingBot/assets/107801980/e113468a-edb1-49ce-8c7c-0ff415987023)

### Opened position on the exchange

![Screenshot 2024-04-25 124425](https://github.com/krzysiekk9/bybitTradingBot/assets/107801980/ce97ab74-7901-4e12-98a7-5f3a82e6ad7e)
