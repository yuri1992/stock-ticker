import logging
from threading import RLock

import yfinance as yf
from cachetools import TTLCache, cached

logger = logging.getLogger(__name__)


class YahooFinanceCache:
    def __init__(self, *args, **kwargs):
        super(YahooFinanceCache, self).__init__(*args, **kwargs)
        self._cache = {}

    def get(self, stock_name):
        return self._cache.get(stock_name)

    def set(self, stock_name, stock):
        self._cache[stock_name] = stock


YahooFinanceCache = YahooFinanceCache()

cache = TTLCache(maxsize=1024, ttl=5)
long_cache = TTLCache(maxsize=1024, ttl=60 * 60 * 12)
lock = RLock()


class LiveStock:
    def __init__(self, stock_name, yfstock=None):
        self.stock_name = stock_name
        self._last_price = None
        if yfstock is None:
            self.data = yf.Ticker(stock_name)


    def __hash__(self):
        return hash(self.stock_name)

    @property
    def name(self):
        return self.stock_name

    @cached(cache)
    def _price(self):
        try:
            close_ = self.data.history(period="1d", interval="1m", auto_adjust=False).Close[-1]
            self._last_price = close_
            return close_
        except Exception as e:
            logger.error(e)
            return None

    @property
    def price(self):
        return self._price()

    @property
    def last_price(self):
        return self._last_price

    @classmethod
    def from_stock_name(cls, stock_name):
        stock = YahooFinanceCache.get(stock_name)
        if not stock:
            stock = LiveStock(stock_name)
            stock.data = yf.Ticker(stock_name)
            YahooFinanceCache.set(stock_name, stock)
            return stock
        return stock

    @cached(long_cache)
    def get_price_at(self, period=None, start=None, end=None, interval="1d", auto_adjust=False):
        return self.data.history(period=period, interval=interval, start=start, end=end, auto_adjust=False)

    def get_close_price(self, period="1d"):
        return self.data.history(period=period, interval="1m", auto_adjust=False).Close[-1]

    def get_open_price(self, period="1d"):
        return self.data.history(period=period, auto_adjust=False).Open[0]
