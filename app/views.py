import logging

from django.http import HttpResponse
from django.views.generic import TemplateView

logger = logging.getLogger(__name__)


def index(request):
    from .runner import Runner
    Runner.runner(force=False)

    logger.info("started via http request")
    return HttpResponse("Started.")


class StatusView(TemplateView):
    template_name = "status.html"
    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)