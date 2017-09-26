# -*- coding: utf-8 -*-
u"""
:mod:`edx_ace.utils.plugins` contains utility functions used
to make working with the ACE plugin system easier. These are intended
for internal use by ACE.
"""
from __future__ import absolute_import, division, print_function

import logging
from functools import partial

from stevedore import enabled

LOG = logging.getLogger(__name__)


def get_manager(namespace, names=None):
    u"""
    Get the stevedore extension manager for this namespace.

    Args:
        namespace (basestring): The entry point namespace to load plugins for.
        names (list): A list of names to load. If this is ``None`` then all extension will be loaded from this
            namespace.

    Returns:
        stevedore.enabled.EnabledExtensionManager: Extension manager with all extensions instantiated.
    """
    return enabled.EnabledExtensionManager(
        namespace=namespace,
        check_func=partial(check_plugin, namespace=namespace, names=names),
        invoke_on_load=True,
    )


def get_plugins(namespace, names=None):
    u"""
    Get all extensions for this namespace and list of names.

    Args:
        namespace (basestring): The entry point namespace to load plugins for.
        names (list): A list of names to load. If this is ``None`` then all extension will be loaded from this
            namespace.

    Returns:
        list: A list of extensions.
    """
    return list(get_manager(namespace, names))


def check_plugin(extension, namespace, names=None):
    u"""
    Check the extension to see if it's enabled.

    Args:
        extension (stevedore.extension.Extension): The extension to check.
        namespace (basestring): The namespace that the extension was loaded from.
        names (list): A whitelist of extensions that should be checked.

    Returns:
        bool: Whether or not this extension is enabled and should be used.
    """
    if names is None or extension.name in names:
        plugin_enabled = extension.plugin.enabled()
        if not plugin_enabled:
            LOG.info(u'Extension with name %s for namespace %s is not enabled', extension.name, namespace)
        return plugin_enabled
    return False
