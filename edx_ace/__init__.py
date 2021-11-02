"""
ACE (Automated Communications Engine) is a framework for automatically
sending messages to users.

:mod:`edx_ace` exports the typical set of functions and classes needed to use
ACE.
"""

from .ace import send
from .channel import Channel, ChannelType
from .message import Message, MessageType
from .policy import Policy, PolicyResult
from .recipient import Recipient
from .recipient_resolver import RecipientResolver

__version__ = '1.4.0'

default_app_config = 'edx_ace.apps.EdxAceConfig'

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
