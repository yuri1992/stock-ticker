import pytest
from django.utils.timezone import now

from app.models import Strategy


@pytest.mark.django_db
class TestAlgorithmBase:
    def test_runner_not_initial_not_needed_strategies(self):
        from app.runner import Runner
        assert not Runner.running_strategies
        assert not Runner.runner()

        Strategy.objects.create(name="bla")
        assert not Runner.running_strategies
        assert not Runner.runner()

    def test_runner_initial_needed_strategies(self):
        from app.runner import Runner
        s = Strategy.objects.create(name="bla", python_kwargs={"run_on_business_days": False})
        assert not Runner.runner()
        assert not Runner.running_strategies

        s.python_model = 'app.strategies.amit_strategy'
        s.save()
        assert not Runner.runner()
        assert not Runner.running_strategies

        s.start_at = now()
        s.save()

        assert Runner.runner()
        assert Runner.running_strategies
        Runner.stop()
