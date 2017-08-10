from abc import ABCMeta

import six
from django.template import loader


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


class EmailRenderer(AbstractRenderer):
    def render(self, message):
        # TODO Get templates from message.type
        message_type = message.type
        templates = {
            'subject': message_type.get_email_subject_template(),
            'body_html': message_type.get_email_body_html_template(),
            'body_text': message_type.get_email_body_text_template(),
        }

        renderings = {}
        for name, template in six.iteritems(templates):
            renderings[name] = loader.get_template(template).render(message.context)

        return renderings
