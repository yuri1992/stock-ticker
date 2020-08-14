import pytest
from django.utils.timezone import now

from app.models import Strategy
from app.strategies.amit_strategy import MyStrategy
from conftest import MockLiveStock
from stocks.datalayer import LiveStock


@pytest.mark.django_db
class TestStrategy1:
    def test_strategy_is_running(self):
        strategy = Strategy.objects.create(name="bla")
        my_strategy_runner = MyStrategy(strategy_name="bla", run_on_business_days=False)
        my_strategy_runner.run()

        assert my_strategy_runner.stock_to_watch
        assert not my_strategy_runner.get_open_stocks()

    def test_strategy_is_selling(self):
        strategy = Strategy.objects.create(name="bla")
        my_strategy_runner = MyStrategy(strategy_name="bla", run_on_business_days=False)
        my_strategy_runner.run()

        stock_to_buy = MockLiveStock("AAPL")
        stock_to_buy.data["price"] = 82.2
        my_strategy_runner.buy_stock(stock_to_buy)

        assert my_strategy_runner.get_open_stocks()
        assert my_strategy_runner.get_all_stocks()

        my_strategy_runner.sell_stock(stock_to_buy)
        assert not my_strategy_runner.get_open_stocks()
        assert my_strategy_runner.get_all_stocks()

    def test_strategy_watching_is_buying_stocks(self):
        strategy = Strategy.objects.create(name="bla")
        my_strategy_runner = MyStrategy(strategy_name="bla", run_on_business_days=False)

        stock_to_buy = MockLiveStock("AAPL")
        stock_to_buy.data["price"] = 82.2
        my_strategy_runner.stock_to_watch.add(stock_to_buy)

        stock_to_buy.data["price"] = 83.2
        my_strategy_runner.watch_stocks()
        assert stock_to_buy.name in my_strategy_runner.stock_watcher


