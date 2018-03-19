# -*- coding: utf-8 -*-
u"""
A diagnostic utility that can be used to render email messages to files on disk.
"""
from __future__ import absolute_import, division, print_function

import errno
import logging
import os
from datetime import datetime

import attr
import six

from edx_ace.channel import Channel, ChannelType

LOG = logging.getLogger(__name__)

PATH_OVERRIDE_KEY = u'output_file_path'
DEFAULT_OUTPUT_FILE_PATH_TPL = u'/edx/src/ace_messages/{recipient.username}.{date:%Y%m%d-%H%M%S}.html'
TEMPLATE = u"""
<!DOCTYPE html>
<html>
    <head>
        {head_html}
    </head>
    <body>
        {body_html}
    </body>
    <!-- to: {email_address} -->
    <!-- from_name: {from_name} -->
    <!-- subject: {subject} -->
    <!-- body: {body} -->
</html>
"""
STDOUT_TEMPLATE = u"""
------- EMAIL -------
To: {email_address}
From: {from_name}
Subject: {subject}
Body:
{body}
-------  END  -------
"""
OUTPUT_ENCODING = u'utf8'


class FileEmailChannel(Channel):
    u"""
    An email channel that simply renders the message HTML to a file and the body text to stdout.

    If you add this channel to your enabled channels list as your email channel, it will write out the text version
    of the email to stdout and the HTML version to an output file.

    Examples::

        ACE_ENABLED_CHANNELS = ['file_email']

    By default it writes the output file to /edx/src/ace_output.html and overwrites any existing file at that location.
    In the edX devstack, this folder is shared between the host and the containers so you can easily open the file using
    a browser on the host. You can override this output file location by passing in a ``output_file_path`` key in the
    message options. That path specifies where in the container filesystem the file should be written.

    Both streams of output are UTF-8 encoded.
    """

    channel_type = ChannelType.EMAIL

    @classmethod
    def enabled(cls):
        u"""
        Returns: True always!
        """
        return True

    def _encode(self, s):  # pragma: no cover
        if six.PY2:
            return s.encode(OUTPUT_ENCODING)
        else:
            return s

    def deliver(self, message, rendered_message):
        template_vars = {k: v.strip() for k, v in attr.asdict(rendered_message).items()}
        template_vars[u'email_address'] = message.recipient.email_address

        rendered_template = TEMPLATE.format(**template_vars)
        output_file_path = message.options.get(PATH_OVERRIDE_KEY, DEFAULT_OUTPUT_FILE_PATH_TPL.format(
            recipient=message.recipient,
            date=datetime.now()
        ))
        make_parent_directories(output_file_path)
        with open(output_file_path, u'w') as output_file:  # pylint: disable=open-builtin
            output_file.write(self._encode(rendered_template))

        print(self._encode(STDOUT_TEMPLATE.format(**template_vars)))


def make_parent_directories(path):
    parent_dir_path = os.path.dirname(os.path.realpath(path))
    try:
        os.makedirs(parent_dir_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(parent_dir_path):
            pass
        else:
            raise
