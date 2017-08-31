from django.dispatch import receiver
from edx_ace.monitoring import report_metric

try:
    import newrelic.agent
except ImportError:
    newrelic = None  # pylint: disable=invalid-name


@receiver(report_metric)
def report_to_newrelic(sender, key, value, **kwargs):
    if newrelic:
        newrelic.agent.add_custom_parameter(key, value)
