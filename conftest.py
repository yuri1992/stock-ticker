import pytest

from app.models import Portfolio, Strategy


@pytest.fixture()
def algorithm_2():
    return Strategy.objects.create(
        name="test2"
    )


@pytest.fixture()
def algorithm_1():
    return Strategy.objects.create(
        name="test1"
    )


@pytest.fixture()
def portfolio():
    return Portfolio.objects.create(
        algo=algorithm_1()
    )


class MockLiveStock:
    def __init__(self, stock_name, yfstock=None):
        self.stock_name = stock_name
        self.data = {}

    @property
    def name(self):
        return self.stock_name

    @property
    def price(self):
        return self.data.get("price")

    @classmethod
    def from_stock_name(cls, stock_name):
        stock = MockLiveStock(stock_name)
        return stock

    def get_close_price(self, period="1d"):
        return self.data.get("close")

    def get_open_price(self, period="1d"):
        return self.data.get("open")
