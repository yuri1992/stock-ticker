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
            s, _ = Strategy.objects.get_or_create(name="strategy1", python_model='app.strategies.amit_strategy')
            s.start_at = now()
            s.save()
            if os.environ.get('RUN_MAIN', None):
                Runner.runner(force=False)
        except:
            pass
