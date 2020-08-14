import logging
import time
from collections import deque
from datetime import timedelta

from bdateutil import isbday
from django.utils.timezone import now

from stocks import utils
from stocks.algorithm import AlgorithmBase
from stocks.background import BackgroundRunner
from stocks.constants import TOP_100_STOCKS
from stocks.utils import get_change

logger = logging.getLogger(__name__)


class MyStrategy(AlgorithmBase, BackgroundRunner):
    def __init__(self, sell_threshold=2, interval=15, percentage_decrease=11, number_of_increase_in_row=4,
                 run_on_business_days=True,
                 *args,
                 **kwargs):
        super(MyStrategy, self).__init__(*args, **kwargs)

        self.sleep_time = 60
        self.sell_threshold = sell_threshold
        self.interval = interval
        # We are checking for stock that decreased in 11%
        self.percentage_decrease = percentage_decrease
        # We are checking for 3 times in a row increase in price between the intervals
        self.number_of_increase_in_row = number_of_increase_in_row

        self.stock_to_watch = set()
        self.stock_watcher = {}

        self.run_on_business_days = run_on_business_days

        self.last_time = None
        self.init()

    def init(self):
        pass

    def run(self):
        if self.run_on_business_days and not isbday(now()):
            logger.info("%s is not a business day, we are going to sleep", now())
            time.sleep(60 * 30)
            return None

        already_purchased_stocks = set()
        self.watch_stock_to_sell(already_purchased_stocks)
        self.watch_stocks()
        self.find_stocks_in_criteria(already_purchased_stocks)

    def watch_stock_to_sell(self, already_purchased_stocks):
        for stock in self.get_open_stocks():
            already_purchased_stocks.add(stock.live)
            change = get_change(stock.live.price, stock.price)
            if change >= self.sell_threshold:
                logger.info("We are bought the stock %s in price of %s sell in price of %s",
                            stock.stock_ticker,
                            stock.price,
                            stock.live.price)
                self.sell_stock(stock.live)

    def find_stocks_in_criteria(self, already_purchased_stocks):
        # loop over all the symbols we want
        for stock in TOP_100_STOCKS:
            if stock in already_purchased_stocks or stock in self.stock_to_watch:
                pass

            hist = stock.data.history(period="1mo", auto_adjust=False)
            price_change = hist.Close[-1] - hist.Close[0]
            percentage_change = utils.get_change(hist.Close[0], hist.Close[-1])
            if price_change < 0 and percentage_change > self.percentage_decrease:
                logger.info("Stock %s entered to the watch list, Price ago %s, Price now %s", stock.name,
                            hist.Close[0], hist.Close[-1])
                self.stock_to_watch.add(stock)

    def watch_stocks(self):
        if self.last_time and now() - self.last_time < timedelta(minutes=self.interval):
            return

        self.last_time = now()
        for stock in self.stock_to_watch:
            if stock.name not in self.stock_to_watch:
                self.stock_watcher[stock.name] = {
                    'history': deque(maxlen=self.number_of_increase_in_row),  # Number of increase we need
                    'history_prices': deque(maxlen=self.number_of_increase_in_row),  # Number of increase we need
                    'last_price': None,
                    'buy_price': None,
                    'sell_price': None,
                }

            # Check when to buy the stock.
            # Get price form yahoo
            current_price = stock.price
            logger.info("Stock %s price now is %s", stock.name, current_price)

            last_price = self.stock_watcher[stock.name].get("last_price")
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
