from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now

from app.models import Strategy, Portfolio, Stock
from stocks.datalayer import LiveStock


class AlgorithmBase:
    def __init__(self, strategy_name=None, *args, **kwargs):
        super(AlgorithmBase, self).__init__()
        self.algo = Strategy.objects.get(name=strategy_name or self.__class__.__name__)


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
        return Stock.objects.create(
            stock_ticker=stock.name,
            quantity=quantity,
            portfolio=self.get_portfolio(),
            price=stock.price,
            current_price=stock.price,
            purchase_at=now()
        )

    def sell_stock(self, stock: LiveStock, quantity=None):
        stock = self.get_portfolio().stock_set.get(stock_ticker=stock.name, sold_at__isnull=True)
        if quantity is None:
            quantity = stock.quantity

        stock.current_price = stock.price
        stock.sold_price = stock.price
        stock.sold_at = now()
        stock.save()

        return stock
