import pytest
from django.utils.timezone import now

from app.models import Strategy, Stock, Portfolio
from stocks.algorithm import AlgorithmBase
from stocks.datalayer import LiveStock


@pytest.mark.django_db
class TestAlgorithmBase:
    def test_runner_not_initial_not_needed_strategies(self):
        s = Strategy.objects.create(name="bla", python_kwargs={"run_on_business_days": False})
        p = Portfolio.objects.create(algo=s)

        stock = LiveStock.from_stock_name("M")

        stock = Stock.objects.create(portfolio=p, quantity=1000, stock_ticker="M", price=stock.price - 1)

        recomendation = AlgorithmBase(s.name).get_momentom(stock)

        assert recomendation == AlgorithmBase.SELL

