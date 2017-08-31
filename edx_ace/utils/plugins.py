import logging
from functools import partial

from stevedore import enabled

LOG = logging.getLogger(__name__)


def get_manager(namespace, names=None):
    return enabled.EnabledExtensionManager(
        namespace=namespace,
        check_func=partial(check_plugin, namespace=namespace, names=names),
        invoke_on_load=True,
    )


def get_plugins(namespace, names=None):
    return list(get_manager(namespace, names))


def check_plugin(extension, namespace, names=None):
    if names is None or extension.name in names:
        plugin_enabled = getattr(extension.plugin, 'enabled', True)
        if not plugin_enabled:
            LOG.info('Extension with name %s for namespace %s is not enabled', extension.name, namespace)
        return plugin_enabled
    return False
