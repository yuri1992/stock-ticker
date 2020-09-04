import importlib
import logging
import signal
from threading import Event

from app.models import Strategy

log = logging.getLogger(__name__)


class Runner:
    def __init__(self):
        self.running_strategies = {}
        self.exit_event = Event()
        self.running = False

        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True
        self.stop()

    def check_status(self):
        for strategy, thread in self.running_strategies.items():
            if not thread.is_alive():
                log.info("Thread %s is not running for strategy %s", thread, strategy)

    def stop(self):
        self.exit_event.set()
        threads = []
        for r in self.running_strategies.values():
            thread = r.thread
            threads.append(thread)
            thread.join()

    @staticmethod
    def run_strategy(strategy, exit_event=Event(), start_thread=False):
        module = getattr(importlib.import_module(strategy.python_model), 'MyStrategy')
        arguments = strategy.python_arguments or ()
        kwargs = strategy.python_kwargs or {}
        thread = module(strategy_name=strategy.name, exit_event=exit_event, *arguments, **kwargs)
        if start_thread:
            thread.start()
        return thread

    def runner(self, force=True):
        strategies = Strategy.objects.filter(start_at__isnull=False)
        
        if not self.running or force:
            self.running = True
            for strategy in strategies:
                if strategy.id in self.running_strategies:
                    continue
    
                try:
                    thread = self.run_strategy(strategy, exit_event=self.exit_event, start_thread=True)
                    self.running_strategies[strategy.id] = thread
                except Exception as e:
                    log.exception("Exception wil running", e)
                    if strategy.id not in self.running_strategies:
                        self.running_strategies.pop(strategy.id, None)
            return self.running_strategies


Runner = Runner()
