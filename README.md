### Algorithmic-Trading-Research

#### Indicators
- CCI
- Price Volume

---

### Backtesting Data Sources

#### Intraday Market Data
Finam is a Russian website that provides data for the stock, futures, ETF and Forex markets. The data is available for only very highlight capitalized securities, however for these securities you can download several months worth of tick data.

Here is how to download stock data:

- Use Google translate to translate this Russian website
- Browse the following URL: https://www.finam.ru/analysis/profile041CA00007/default.asp
- In the top form, select "U.S. Stocks (BATS)" then select a stock (Example: Exxon Mobil)
- Select the start/end dates and frequency (Example: 20.04.2012 -> 24.04.2012 and tick data)
- Click on the "Get the file" button to download stock data in CSV format

#### Interday Market Data
Yahoo was also listed in the previous article and it is one of most used data sources for stock data.
It allows you to download interday data for several stock markets.

Here is an example how to import stock data:

```
from pandas_datareader import data

start_date = "2018-01-01"
end_date = "2022-01-01"
goog_data = data.DataReader("GOOG", "yahoo", start_date, end_date)
```
