import logging

from stocks import utils
from stocks.algorithm import AlgorithmBase
from stocks.background import BackgroundRunner
from stocks.constants import TOP_1000_STOCKS
from stocks.utils import run_async

logger = logging.getLogger(__name__)


class MyStrategy(AlgorithmBase, BackgroundRunner):

    def __init__(self, sell_threshold=2, interval=15, percentage_decrease=10, number_of_increase_in_row=4,
                 run_on_business_days=False,
                 *args,
                 **kwargs):
        super(MyStrategy, self).__init__(*args, **kwargs)

        self.sleep_time = 60
        self.sell_threshold = sell_threshold
        self.interval = interval

        # We are checking for stock that decreased in 11%
        self.percentage_decrease = percentage_decrease
        self.STOCK_LIST = TOP_1000_STOCKS

        self.iteration = 0

        self.run_on_business_days = run_on_business_days

        self.last_time = None
        self.init()

    def init(self):
        pass

    @run_async
    def check_stock_in_criteria(self, stock):
        try:
            hist = stock.data.history(period="1mo", auto_adjust=False)
            current_price = stock.price
            price_change = current_price - hist.Close[0]
            percentage_change = utils.get_change(hist.Close[0], current_price)
            """
                Checking if the stock has a decrese momentom in the last month.
                checking if the stock has decrease more than %self.percentage_decrease
            """
            if price_change < 0 and percentage_change > self.percentage_decrease:
                logger.info(
                    "Stock %s entered to the watch list, Price at before corona peak ago %s, Price now %s change: %s",
                    stock.name,
                    hist.Close[0],
                    current_price,
                    percentage_change)

                self.stock_to_watch.add(stock)
        except Exception as e:
            logger.warn("Error getting data about %s: %s", stock.name, e)
