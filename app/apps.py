import os

from django.apps import AppConfig


class AppConfig(AppConfig):
    name = 'app'

    def ready(self):
        try:
            # importing model classes
            from .runner import Runner  # or...
            from .models import Strategy  # or...
            s = Strategy.objects.get_or_create(name="strategy1", python_model='app.strategies.amit_strategy')
            if os.environ.get('RUN_MAIN', None):
                Runner.runner(force=False)
        except:
            pass
