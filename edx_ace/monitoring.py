from django.dispatch import Signal

# Signal for reporting metrics
# Can be used by applications to support their own monitoring tools.
report_metric = Signal(providing_args=['key', 'value'])


def report(key, value):
    report_metric.send(sender=None, key=key, value=value)
