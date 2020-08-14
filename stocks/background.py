import time
from threading import Event, Thread


class BackgroundRunner:
    def __init__(self, exit_event=None, *args, **kwargs):
        super(BackgroundRunner, self).__init__(*args, **kwargs)
        self.exit_event = exit_event or Event()
        self.thread = None
        self.sleep_time = 60

    def start(self):
        self.thread = Thread(target=self._run)
        self.thread.start()
        return self.thread

    def run(self):
        raise NotImplemented

    def _run(self):
        while not self.exit_event.is_set():
            self.run()
            time.sleep(self.sleep_time)
