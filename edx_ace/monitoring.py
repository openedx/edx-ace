try:
    import newrelic.agent
except ImportError:
    newrelic = None  # pylint: disable=invalid-name


def report(key, value):
    report_to_newrelic(key, value)


def report_to_newrelic(key, value):
    if newrelic:
        newrelic.agent.add_custom_parameter(key, value)
