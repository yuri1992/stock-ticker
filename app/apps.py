import os

from django.apps import AppConfig
from django.utils.timezone import now


class AppConfig(AppConfig):
    name = 'app'

    def ready(self):
        try:
            # importing model classes
            from .runner import Runner  # or...
            from .models import Strategy  # or...
            s, _ = Strategy.objects.get_or_create(python_model='app.strategies.amit_strategy')
            s.name = "Original Strategy"
            s.start_at = now()
            s.save()

            s, _ = Strategy.objects.get_or_create(python_model='app.strategies.corona_watcher')
            s.name = "Pick up stock that didn't recovered from corona"
            s.start_at = now()
            s.save()

            s, _ = Strategy.objects.get_or_create(python_model='app.strategies.fast_strategy')
            s.start_at = now()
            s.name = "Fast buy and sell"
            s.description = "Buy after 2 times increase, check every 1 minute, sell after 0.5%, stock poll is all stock increased from the last 5 days"
            s.save()
            # if os.environ.get('RUN_MAIN', None):
            #     Runner.runner(force=False)
        except:
            pass
