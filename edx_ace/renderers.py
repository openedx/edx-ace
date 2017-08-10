from abc import ABCMeta

import six
from django.template import loader
from edx_ace.channel import ChannelType


class AbstractRenderer(object):
    """
    Base class for message renderers.

    A message renderer is responsible for taking a one, or more, templates, and context, and outputting
    a rendered message for a specific message channel (e.g. email, SMS, push notification).
    """
    __metaclass__ = ABCMeta

    def render(self, message):
        """
        Renders the given message.

        Args:
             message (Message)

         Returns:
             dict: Mapping of template names/types to rendered text.
        """
        raise NotImplementedError

    def get_template_for_message(self, message, filename):
        template_path = "{msg.app_label}/edx_ace/{msg.name}/{channel.value}/{filename}".format(
            msg=message,
            channel=self.channel,
            filename=filename,
        )
        return loader.get_template(template_path)


class EmailRenderer(AbstractRenderer):
    channel = ChannelType.EMAIL

    def render(self, message):
        templates = {
            'subject': self.get_template_for_message(message, 'subject.txt'),
            'body_html': self.get_template_for_message(message, 'body.html'),
            'body_text': self.get_template_for_message(message, 'body.txt'),
        }

        renderings = {}
        for name, template in six.iteritems(templates):
            renderings[name] = template.render(message.context)

        return renderings
