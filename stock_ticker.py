from constants import TOP_100_STOCKS_SYMBOLS
import yfinance as yf


def get_ticker(symbol):
    return yf.Ticker(symbol)


def get_tickers(symbols: list):
    return yf.Tickers(" ".join(x.lower() for x in symbols))


def get_highest_stock(symbols):
    for ticker in get_tickers(symbols):
        ticker.dividends


if __name__ == '__main__':
    pass
