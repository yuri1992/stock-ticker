from django.contrib import admin

from .models import Portfolio, Stock, Strategy

admin.site.register(Portfolio)
admin.site.register(Stock)
admin.site.register(Strategy)
