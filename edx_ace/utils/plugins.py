from stevedore import enabled


def get_plugins(namespace, names=None):
    return enabled.EnabledExtensionManager(
        namespace=namespace,
        check_func=lambda name: True if names is None else name in names,
    )
