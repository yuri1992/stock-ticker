import time

import yfinance as yf
from collections import deque

# Interval in seconds for checking
SELL_THRESHOLD = 2
INTERVAL = 60 * 15

# We are checking for stock that decreased in 11%
PERCENTAGE_DECREASE = 5

# We are checking for 3 times in a row increase in price between the intervals
NUMBER_OF_INCREASE_IN_ROW = 4


def get_change(current, previous):
    if current == previous:
        return 0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return float('inf')


TOP_100_STOCKS_SYMBOLS = [
    "ATVI", "ADBE", "AMD", "ALXN", "ALGN", "GOOG", "GOOGL", "AMZN", "AMGN", "ADI", "ANSS", "AAPL",
    "AMAT", "ASML", "ADSK", "ADP", "BIDU", "BIIB", "BMRN", "BKNG", "AVGO", "CDNS", "CDW", "CERN",
    "CHTR", "CHKP", "CTAS", "CSCO", "CTXS", "CTSH", "CMCSA", "CPRT", "CSGP", "COST", "CSX",
    "DXCM", "DOCU", "DLTR", "EBAY", "EA", "EXC", "EXPE", "FB", "FAST", "FISV", "FOX", "FOXA",
    "GILD", "IDXX", "ILMN", "INCY", "INTC", "INTU", "ISRG", "JD", "KLAC", "LRCX", "LBTYA",
    "LBTYK", "LULU", "MAR", "MXIM", "MELI", "MCHP", "MU", "MSFT", "MDLZ", "MNST", "NTAP", "NTES",
    "NFLX", "NVDA", "NXPI", "ORLY", "PCAR", "PAYX", "PYPL", "PEP", "QCOM", "REGN", "ROST", "SGEN",
    "SIRI", "SWKS", "SPLK", "SBUX", "SNPS", "TMUS", "TTWO", "TSLA", "TXN", "KHC", "TCOM", "ULTA",
    "VRSN", "VRSK", "VRTX", "WBA", "WDC", "WDAY", "XEL", "XLNX", "ZM", "TQQQ"
]

stock_to_investigate = []

# loop over all the symbols we want
for stock in TOP_100_STOCKS_SYMBOLS:
    ticker = yf.Ticker(stock)

    # get historical market data
    hist = ticker.history(period="1mo")

    price_change = hist.Close[0] - hist.Close[-1]

    if price_change > 0:
        print("{}: Price change is {}".format(stock, price_change))
        stock_to_investigate.append((stock, hist))

stock_to_watch = []

for t in stock_to_investigate:
    stock_name, stock_hist = t
    percentage_change = get_change(stock_hist.Close[0], stock_hist.Close[-1])
    if percentage_change > PERCENTAGE_DECREASE:
        print("The following".format(stock_hist))
        stock_to_watch.append(t)

stock_watcher = {}

while True:
    for t in stock_to_watch:
        stock_name, stock_hist = t

        if stock_name not in stock_watcher:
            stock_watcher[stock_name] = {
                'history': deque(maxlen=NUMBER_OF_INCREASE_IN_ROW),  # Number of increase we need
                'history_prices': deque(maxlen=NUMBER_OF_INCREASE_IN_ROW),  # Number of increase we need
                'last_price': None,
                'buy_price': None,
                'sell_price': None,
            }

        # Check when to buy the stock.
        # Get price form yahoo
        current_price = yf.Ticker(stock_name).history(period="1s").Close[0]
        print("Stock {} price now is {}".format(stock_name, current_price))

        buy_price = stock_watcher[stock_name].get('buy_price')
        if buy_price:
            # Checking when to sell the stock.
            change = get_change(buy_price, current_price)
            print("Stock {} has a change of {}%".format(stock_name, change))
            if change >= SELL_THRESHOLD:
                print("We are bought the stock {} in price of {} sell in price of {}".format(stock_name, buy_price,
                                                                                             current_price))
                stock_watcher[stock_name]['sell_price'] = current_price
        else:
            last_price = stock_watcher[stock_name].get("last_price")
            if last_price:
                if current_price > last_price:
                    stock_watcher[stock_name].get('history').append(True)
                elif current_price == last_price:
                    # if the interval is 15m it should be false.
                    pass
                else:
                    stock_watcher[stock_name].get('history').append(False)

            # Set last price
            stock_watcher[stock_name]['last_price'] = current_price
            stock_watcher[stock_name]['history_prices'].append(current_price)

            if all(list(stock_watcher[stock_name]['history'])) and len(
                    list(stock_watcher[stock_name]['history'])) == NUMBER_OF_INCREASE_IN_ROW:
                print("Stock {} Price increase {} times in the last {}".format(stock_name, NUMBER_OF_INCREASE_IN_ROW, INTERVAL))
                stock_watcher[stock_name]['buy_price'] = current_price

    time.sleep(INTERVAL)
