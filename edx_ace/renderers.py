from abc import ABCMeta, abstractmethod
from collections import namedtuple

import six
from django.template import loader
from edx_ace.channel import ChannelType


@six.add_metaclass(ABCMeta)
class AbstractRenderer(object):
    """
    Base class for message renderers.

    A message renderer is responsible for taking a one, or more, templates, and context, and outputting
    a rendered message for a specific message channel (e.g. email, SMS, push notification).
    """

    @abstractmethod
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


RenderedEmail = namedtuple('RenderedEmail', [
    'from_name',
    'subject',
    'body_html',
    'head_html',
    'body_text',
])


class EmailRenderer(AbstractRenderer):
    channel = ChannelType.EMAIL
    rendered_message_cls = RenderedEmail
    template_names = RenderedEmail(
        from_name='from_name.txt',
        subject='subject.txt',
        body_html='body.html',
        head_html='head.html',
        body_text='body.txt',
    )

    def render(self, message):
        templates = self.rendered_message_cls(*(
            self.get_template_for_message(message, name)
            for name in self.template_names
        ))

        # TODO(later): all renderers will need this, won't they?
        renderings = self.rendered_message_cls(*(
            template.render(message.context)
            for template in templates
        ))

        return renderings
