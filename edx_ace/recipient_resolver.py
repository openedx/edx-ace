import six

from abc import ABCMeta, abstractmethod
from edx_ace.ace_step import ACEStep


# TODO(now): Do we even need to define this class? It seems like something the client could manage on their own.
@six.add_metaclass(ABCMeta)
class RecipientResolver(ACEStep):

    @abstractmethod
    def send(self, msg_type, *args, **kwargs):
        pass
