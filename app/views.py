import logging
from threading import Thread

from django.http import HttpResponse
from django.views.generic import TemplateView
from .runner import Runner

logger = logging.getLogger(__name__)


def index(request):
    Thread(target=Runner.runner, kwargs={"force": False}).start()
    logger.info("started via http request")
    return HttpResponse("Started.")


class StatusView(TemplateView):
    template_name = "status.html"

    def get_context_data(self, **kwargs):
        ctx =  super().get_context_data(**kwargs)

        ctx['strategies'] = Runner.running_strategies
        ctx['runner'] = Runner

        return ctx