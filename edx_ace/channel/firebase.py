# -*- coding: utf-8 -*-
u"""
A diagnostic utility that can be used to render email messages to files on disk.
"""
from __future__ import absolute_import, division, print_function

import logging

from django.conf import settings
try:
    from pyfcm import FCMNotification
    _pyfcm_imported = True
except ImportError:
    _pyfcm_imported = False

from edx_ace.channel import Channel, ChannelType

LOG = logging.getLogger(__name__)


class FirebaseChannel(Channel):

    channel_type = ChannelType.PUSH

    @classmethod
    def enabled(cls):
        return _pyfcm_imported and getattr(settings, 'ACE_CHANNEL_FIREBASE_API_KEY', None) is not None

    def deliver(self, message, rendered_message):
        push_service = FCMNotification(api_key=settings.ACE_CHANNEL_FIREBASE_API_KEY)
        result = push_service.notify_single_device(
            registration_id=message.recipient.mobile_device_id,
            message_title=rendered_message.title.strip(),
            message_body=rendered_message.body.strip(),
        )
        print(result)
