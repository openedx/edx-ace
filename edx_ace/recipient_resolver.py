u"""
:mod:`edx_ace.recipient_resolver` contains the :class:`RecipientResolver`, which facilitates
a design pattern that separates message content from recipient lists.
"""
from __future__ import absolute_import

from abc import ABCMeta, abstractmethod

import six


# TODO(now): Do we even need to define this class? It seems like something the client could manage on their own.
@six.add_metaclass(ABCMeta)
class RecipientResolver(object):
    u"""
    This class represents a pattern for separating the content of a message
    (the :class:`.MessageType`) from the selection of recipients (the :class:`RecipientResolver`).
    """
    @abstractmethod
    def send(self, msg_type, *args, **kwargs):
        u"""
        :func:`.send` a :class:`.Message` personalized from ``msg_type`` to all
        recipients selected by this :class:`.RecipientResolver`.

        Arguments:
            msg_type (:class:`.MessageType`): An instantiated :class:`.MessageType`
                that describes the message batch to send.
        """
        pass
