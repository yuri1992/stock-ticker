import pytest

from stocks.datalayer import LiveStock
from stocks.algorithm import AlgorithmBase


@pytest.mark.django_db
class TestAlgorithmBase:
    def test_algo_name(self, algorithm_1):
        o = AlgorithmBase(algorithm_1.name)
        assert o.algo.id == algorithm_1.id
        assert not o.get_all_stocks()
        assert not o.get_open_stocks()

    def test_buy_and_sell(self, algorithm_1, algorithm_2):
        o = AlgorithmBase(algorithm_1.name)
        assert o.algo.id == algorithm_1.id

        appl = LiveStock.from_stock_name("AAPL")
        stock = o.buy_stock(appl)
        assert stock.purchase_at
        assert not stock.sold_at
        assert len(o.get_all_stocks()) == 1
        assert o.get_all_stocks()[0].stock_ticker == "AAPL"
        assert o.get_open_stocks()[0].stock_ticker == "AAPL"

        f = AlgorithmBase(algorithm_2.name)
        assert f.algo.id == algorithm_2.id
        assert not f.get_all_stocks()

        stock = o.sell_stock(appl)
        assert stock.sold_at
        assert not o.get_open_stocks()



