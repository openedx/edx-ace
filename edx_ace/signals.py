from django.dispatch import receiver

from .monitoring import report_metric

try:
    import newrelic.agent
except ImportError:
    newrelic = None  # pylint: disable=invalid-name


@receiver(report_metric)
def report_to_newrelic(sender, key, value, **kwargs):  # pylint: disable=unused-argument
    if newrelic:
        newrelic.agent.add_custom_parameter(key, value)
