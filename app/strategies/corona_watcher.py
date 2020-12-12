import logging

from stocks import utils
from stocks.algorithm import AlgorithmBase
from stocks.background import BackgroundRunner
from stocks.constants import TOP_1000_STOCKS
from stocks.utils import run_async

logger = logging.getLogger(__name__)


class MyStrategy(AlgorithmBase, BackgroundRunner):
    STOCK_LIST = TOP_1000_STOCKS

    def __init__(self, sell_threshold=2, interval=15, percentage_decrease=11, number_of_increase_in_row=4,
                 run_on_business_days=False,
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
        self.last_time_find_criteria = None
        self.init()

    def init(self):
        pass

    @run_async
    def check_stock_in_criteria(self, stock):
        try:
            price_now = stock.price
            corona_price = stock.data.history(start="2020-03-23", end="2020-03-24", auto_adjust=False).Close[0]
            price_before_corona = stock.data.history(start="2020-01-23", end="2020-01-24", auto_adjust=False).Close[0]

            if price_now < price_before_corona and \
                    utils.get_change(price_now, price_before_corona) > 30 and \
                    corona_price > price_now:
                logger.info("Stock %s entered to the watch list, Price ago %s, Price now %s, Price at CoronaPeak %s",
                            stock.name,
                            price_before_corona,
                            price_now,
                            corona_price)

                self.stock_to_watch.add(stock)
        except Exception as e:
            logger.warn("Error getting data about %s: %s", stock.name, e)
