import logging
import time
from collections import deque
from datetime import timedelta

from bdateutil import isbday
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now

from app.models import Strategy, Portfolio, Stock
from stocks.datalayer import LiveStock
from stocks.utils import get_change

SELL_BEFORE_CLOSE_FACTOR = 0.9

logger = logging.getLogger(__name__)


class AlgorithmBase:
    STOCK_PRICE_BUCKET = 2500

    def __init__(self, strategy_name=None, sell_threshold=2, interval=4, *args, **kwargs):
        super(AlgorithmBase, self).__init__()
        self.algo = Strategy.objects.get(name=strategy_name or self.__class__.__name__)
        self.iteration = 0

        self.sleep_time = 60
        self.sell_threshold = sell_threshold
        self.stop_sell_threshold = 2
        self.interval = interval

        # We are checking for 3 times in a row increase in price between the intervals
        self.number_of_increase_in_row = 4

        self.last_time = None
        self.last_time_find_criteria = None

        self.stock_to_watch = set()
        self.stock_watcher = {}

        self.run_on_business_days = False

        self.STOCK_LIST = []

    def get_portfolio(self):
        try:
            return self.algo.portfolio
        except ObjectDoesNotExist as e:
            return Portfolio.objects.create(algo=self.algo)

    def get_all_stocks(self):
        return self.get_portfolio().stock_set.all()

    def get_open_stocks(self):
        return self.get_portfolio().stock_set.filter(sold_at__isnull=True)

    def buy_stock(self, stock: LiveStock, quantity=1000):
        if Stock.objects.filter(stock_ticker=stock.name, sold_at__isnull=True).exists():
            logger.info("Can't buy a stock which already in protfolio ")
            return None

        quantity = max(int(self.STOCK_PRICE_BUCKET / stock.price), 1)
        return Stock.objects.create(
            stock_ticker=stock.name,
            quantity=quantity,
            portfolio=self.get_portfolio(),
            price=stock.price,
            current_price=stock.price,
            purchase_at=now()
        )

    def sell_stock(self, stock: LiveStock, quantity=None):
        for stock_db in self.get_portfolio().stock_set.filter(stock_ticker=stock.name, sold_at__isnull=True):
            stock_db.current_price = stock.price
            stock_db.sold_price = stock.price
            stock_db.sold_at = now()
            stock_db.save(update_fields=['current_price', 'sold_price', 'sold_at'])

        return stock

    def clear_stock_history(self, stock):
        self.stock_watcher[stock.name] = {
            'history': deque(maxlen=self.number_of_increase_in_row),  # Number of increase we need
            'history_prices': deque(maxlen=self.number_of_increase_in_row),  # Number of increase we need
            'last_price': None,
            'buy_price': None,
            'sell_price': None,
        }

    def is_trading_day(self):
        return isbday(now())

    def is_trade_open(self):
        d = now()
        return isbday(d) and (d.hour > 14 or (d.hour == 14 and d.minute > 30))

    def time_to_trade_open(self):
        d = now()
        if d.hour >= 21:
            return now().replace(hour=14, minute=30, second=0, microsecond=0) + timedelta(days=1) - now()

        return now().replace(hour=14, minute=30, second=0, microsecond=0) - now()

    def time_to_trade_close(self):
        if not self.is_trade_open():
            return None

        market_close = now().replace(hour=21, minute=0, second=0, microsecond=0)
        return market_close - now()

    def watch_stock_to_sell(self, already_purchased_stocks):
        if not self.is_trade_open():
            return

        for stock in self.get_open_stocks():
            already_purchased_stocks.add(stock.live)
            change = get_change(stock.live.price, stock.price)
            if change >= self.sell_threshold and stock.price < stock.live.price:
                logger.info("We are bought the stock %s in price of %s sell in price of %s",
                            stock.stock_ticker,
                            stock.price,
                            stock.live.price)
                self.sell_stock(stock.live)
            elif change >= self.stop_sell_threshold and stock.price > stock.live.price:
                logger.info("Selling in lose, We are bought the stock %s in price of %s sell in price of %s",
                            stock.stock_ticker,
                            stock.price,
                            stock.live.price)
                self.sell_stock(stock.live)
            elif self.is_trade_open() and self.time_to_trade_close() < timedelta(hours=1):
                """
                    We want to sell before day close,
                    We will sell stock we have a positve change even if it's not in the threshold
                """
                if change >= (self.sell_threshold * SELL_BEFORE_CLOSE_FACTOR) and stock.price < stock.live.price:
                    logger.info("Sell before close, We are bought the stock %s in price of %s sell in price of %s",
                                stock.stock_ticker,
                                stock.price,
                                stock.live.price)
                    self.sell_stock(stock.live)

    def find_stocks_in_criteria(self, already_purchased_stocks):
        if self.last_time_find_criteria and now() - self.last_time_find_criteria < timedelta(minutes=self.interval):
            return

        if not already_purchased_stocks:
            already_purchased_stocks = set()

        # loop over all the symbols we want
        for stock in self.STOCK_LIST:
            if stock in already_purchased_stocks or stock in self.stock_to_watch:
                continue
            self.check_stock_in_criteria(stock)

        self.last_time_find_criteria = now()

    def check_stock_in_criteria(self, stock):
        raise NotImplemented

    def watch_stocks(self):
        if not self.is_trade_open():
            return

        if not self.stock_to_watch:
            return

        if self.last_time and now() - self.last_time < timedelta(minutes=3):
            return

        self.last_time = now()
        for stock in list(self.stock_to_watch):
            if stock.name not in self.stock_watcher:
                self.clear_stock_history(stock)

            # Check when to buy the stock.
            # Get price form yahoo
            last_price = self.stock_watcher[stock.name].get("last_price")
            current_price = stock.price
            logger.info("Stock %s price now is %s, last price was %s", stock.name, current_price, last_price)

            if last_price:
                if current_price > last_price:
                    self.stock_watcher[stock.name].get('history').append(True)
                elif current_price == last_price:
                    # if the interval is 15m it should be false.
                    pass
                else:
                    self.stock_watcher[stock.name].get('history').append(False)

            # Set last price
            self.stock_watcher[stock.name]['last_price'] = current_price
            self.stock_watcher[stock.name]['history_prices'].append(current_price)

            if all(list(self.stock_watcher[stock.name]['history'])) and len(
                    list(self.stock_watcher[stock.name]['history'])) == self.number_of_increase_in_row:
                logger.info("Stock %s Price increase %s times in the last %s", stock.name,
                            self.number_of_increase_in_row,
                            self.interval)
                self.buy_stock(stock)
                self.stock_to_watch.remove(stock)

    def run(self):
        if self.run_on_business_days and not self.is_trading_day():
            trade_open = self.time_to_trade_open()
            logger.info("%s is  not a business day, we are going to sleep, trade will open in %s", now(), trade_open)
            time.sleep(60 * 30)
            return None

        already_purchased_stocks = set()
        self.watch_stock_to_sell(already_purchased_stocks)
        self.watch_stocks()
        self.find_stocks_in_criteria(already_purchased_stocks)
