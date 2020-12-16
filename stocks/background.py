import logging
import time
from threading import Event, Thread

from django.utils.timezone import now

logger = logging.getLogger(__name__)


class BackgroundRunner:
    def __init__(self, exit_event=None, *args, **kwargs):
        super(BackgroundRunner, self).__init__(*args, **kwargs)
        self.exit_event = exit_event or Event()
        self.thread = None
        self.sleep_time = 60
        self.iteration = 0

    def start(self):
        self.thread = Thread(target=self._run)
        # self.thread.daemon = True
        self.thread.start()
        return self.thread

    def run(self):
        logger.info("%s Iteration %s started at %s ", self.__class__.__name__, self.iteration, now())
        self.iteration += 1

    def _run(self):
        while not self.exit_event.is_set():
            self.run()
            self.exit_event.wait(self.sleep_time)
