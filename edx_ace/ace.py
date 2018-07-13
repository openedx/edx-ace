# -*- coding: utf-8 -*-
u"""
The main entry point for sending messages with ACE.

Usage:

.. code-block:: python

    from edx_ace import ace
    from edx_ace.messages import Message

    msg = Message(
        name="test_message",
        app_label="my_app",
        recipient=Recipient(username='a_user', email='a_user@example.com'),
        language='en',
        context={
            'stuff': 'to personalize the message',
        }
    )
    ace.send(msg)
"""

from __future__ import absolute_import, division, print_function

import six

from edx_ace import delivery, policy, presentation
from edx_ace.channel import get_channel_for_message
from edx_ace.errors import ChannelError, UnsupportedChannelError


def send(msg, return_status=False):
    u"""
    Send a message to a recipient.

    Calling this method will result in an attempt being made to deliver the provided message to the recipient. Depending
    on the configured policies, it may be transmitted to them over one or more channels (email, sms, push etc).

    The message must have valid values for all required fields in order for it to be sent. Different channels have
    different requirements, so care must be taken to ensure that all of the needed information is present in the message
    before calling ``ace.send()``.

    Args:
        msg (Message): The message to send.
        return_status (bool): Whether this function should return the

    Returns
        status (list): A list of success/failure status for each channel type
    """
    status = []
    msg.report_basics()

    channels_for_message = policy.channels_for(msg)

    for channel_type in channels_for_message:
        try:
            channel = get_channel_for_message(channel_type, msg)
        except UnsupportedChannelError:
            status.append((channel_type, "UnsupportedChannelError"))
            continue

        try:
            rendered_message = presentation.render(channel, msg)
            status_report = delivery.deliver(channel, rendered_message, msg)
            status.append((channel_type, status_report))
        except ChannelError as error:
            status.append((channel_type, "ChannelError"))
            msg.report(
                u'{channel_type}_error'.format(channel_type=channel_type),
                six.text_type(error)
            )

    # TODO: REMOVE. Is it weird to have a method optionally return?
    # I wanted to make sure any code calling send() won't be confused by a
    # return statement but I don't think any method is trying to assign
    # send() to anything
    if return_status:
        return status
