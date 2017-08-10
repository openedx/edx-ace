from functools import partial
import logging
from stevedore import enabled


LOG = logging.getLogger(__name__)


def get_plugins(namespace, names=None, instantiate=False):
    return {
        extension.name: extension.plugin() if instantiate else extension.plugin
        for extension in enabled.EnabledExtensionManager(
            namespace=namespace,
            check_func=partial(check_plugin, namespace=namespace, names=names),
        )
    }


def check_plugin(extension, namespace, names=None):
    if names is None or extension.name in names:
        enabled = getattr(extension, 'enabled', True)
        if not enabled:
            LOG.info("Extension with name %s for namespace %s is not enabled", extension.name, namespace)
    return False
