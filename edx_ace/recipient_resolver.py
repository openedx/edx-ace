from abc import ABCMeta, abstractmethod

import six


# TODO(now): Do we even need to define this class? It seems like something the client could manage on their own.
@six.add_metaclass(ABCMeta)
class RecipientResolver(object):
    @abstractmethod
    def send(self, msg_type, *args, **kwargs):
        pass
