u"""
ACE (Automated Communications Engine) is a framework for automatically
sending messages to users.

:mod:`edx_ace` exports the typical set of functions and classes needed to use
ACE.
"""
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from .ace import send
from .channel import Channel, ChannelType
from .message import Message, MessageType
from .policy import Policy, PolicyResult
from .recipient import Recipient
from .recipient_resolver import RecipientResolver

__version__ = u'0.1.14'

default_app_config = u'edx_ace.apps.EdxAceConfig'

__all__ = [
    u'send',
    u'__version__',
    u'Message',
    u'MessageType',
    u'Recipient',
    u'RecipientResolver',
    u'ChannelType',
    u'Channel',
    u'Policy',
    u'PolicyResult',
]
