"""
ACE (Automated Communications Engine) is a framework for automatically
sending messages to users.

:mod:`edx_ace` exports the typical set of functions and classes needed to use
ACE.
"""

from importlib.metadata import version

from .ace import send
from .channel import Channel, ChannelType
from .message import Message, MessageType
from .policy import Policy, PolicyResult
from .recipient import Recipient
from .recipient_resolver import RecipientResolver

__version__ = version("edx-ace")


__all__ = [
    'send',
    '__version__',
    'Message',
    'MessageType',
    'Recipient',
    'RecipientResolver',
    'ChannelType',
    'Channel',
    'Policy',
    'PolicyResult',
]
