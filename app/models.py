from django.db import models
from jsonfield import JSONField


class Strategy(models.Model):
    name = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    start_at = models.DateTimeField(null=True)
    is_disabled = models.BooleanField(default=False)

    # python algo.py *args **kwargs we default will use run function
    python_model = models.CharField(max_length=1024)
    python_arguments = JSONField(null=True, blank=True)
    python_kwargs = JSONField(null=True, blank=True)


class Portfolio(models.Model):
    algo = models.OneToOneField(Strategy, on_delete=models.CASCADE)


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
