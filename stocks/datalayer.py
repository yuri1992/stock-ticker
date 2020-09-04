import yfinance as yf


class YahooFinanceMixin:
    def __init__(self, *args, **kwargs):
        super(YahooFinanceMixin, self).__init__(*args, **kwargs)
        self._cache = {}

    def get_stock(self, stock_name):
        if stock_name not in self._cache:
            self._cache[stock_name] = LiveStock.from_stock_name(stock_name)
        return self._cache[stock_name]


class LiveStock:
    def __init__(self, stock_name, yfstock=None):
        self.stock_name = stock_name
        if yfstock is None:
            self.data = yf.Ticker(stock_name)

    def __hash__(self):
        return hash(self.stock_name)

    @property
    def name(self):
        return self.stock_name

    @property
    def price(self):
        return self.data.history(period="1d", auto_adjust=False).Close[0]

    @classmethod
    def from_stock_name(cls, stock_name):
        stock = LiveStock(stock_name)
        stock.data = yf.Ticker(stock_name)
        return stock

    def get_close_price(self, period="1d"):
        return self.data.history(period=period, auto_adjust=False).Close[0]

    def get_open_price(self, period="1d"):
        return self.data.history(period=period, auto_adjust=False).Open[0]