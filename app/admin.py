from django.contrib import admin

from stocks.utils import get_change
from .models import Portfolio, Stock, Strategy


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('info', 'total_profit', 'stock_open_len')

    def info(self, obj):
        return obj



@admin.register(Strategy)
class StrategyAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'start_at', 'python_model', 'total_profit')

    def total_profit(self, obj):
        return obj.portfolio.total_profit()


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('stock_ticker', 'purchase_at', 'price', 'sold_price', 'sold_at', 'change', 'portfolio_info')
    date_hierarchy = 'purchase_at'

    def portfolio_info(self, obj):
        return obj.portfolio

    def change(self, obj):
        if obj.sold_price:
            res = f"{round(get_change(obj.price, obj.sold_price), 2)}%"
            if obj.sold_price < obj.price:
                res = "-" + res
            return res
        return None
