from django.db import models
from django.utils import formats
from jsonfield import JSONField


class Strategy(models.Model):
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=1024, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    start_at = models.DateTimeField(null=True)
    is_disabled = models.BooleanField(default=False)

    # python algo.py *args **kwargs we default will use run function
    python_model = models.CharField(max_length=1024)
    python_arguments = JSONField(null=True, blank=True)
    python_kwargs = JSONField(null=True, blank=True)


class Portfolio(models.Model):
    algo = models.OneToOneField(Strategy, on_delete=models.CASCADE)

    def total_profit(self):
        total = 0
        for stock in self.stock_set.filter(sold_at__isnull=False):
            total += stock.profit()
        return total

    def open_stocks(self):
        return self.stock_set.filter(sold_at__isnull=False)

    @property
    def stock_open_len(self):
        return len(self.open_stocks())

    def __str__(self):
        return f"Algorithm {self.algo.name}, Total Profit: {self.total_profit()}"

class Stock(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    stock_ticker = models.CharField(max_length=128, null=False)
    quantity = models.IntegerField(null=False)
    price = models.DecimalField(null=False, decimal_places=3, max_digits=10)
    current_price = models.DecimalField(null=True, decimal_places=3, max_digits=10)
    sold_price = models.DecimalField(null=True, decimal_places=3, max_digits=10)
    purchase_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    sold_at = models.DateTimeField(null=True)

    @property
    def live(self):
        from stocks.datalayer import LiveStock
        return LiveStock.from_stock_name(self.stock_ticker)

    def profit(self):
        if self.sold_price:
            return (self.sold_price - self.price) * self.quantity
        return 0

    def __str__(self):
        purchase_fmt = formats.date_format(self.purchase_at, "SHORT_DATETIME_FORMAT")
        res = f"Stock {self.stock_ticker}, Buy Price: {self.price}, Buy Date: {purchase_fmt}"
        if self.sold_price:
            sold_fmt = formats.date_format(self.sold_at, "SHORT_DATETIME_FORMAT")
            res += f" Sold at {self.sold_price}, at {sold_fmt}"
        return res