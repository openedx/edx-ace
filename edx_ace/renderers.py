u"""
:mod:`edx_ace.renderers` contains the classes used by ACE to
render messages for particular types of delivery channels. Each
:class:`ChannelType` has a distinct subclass of :class:`AbstractRenderer`
associated with it, which is used to render messages for all
:class:`Channel` subclasses of that type.
"""
from __future__ import absolute_import

import attr

from django.template import loader


class AbstractRenderer(object):
    u"""
    Base class for message renderers.

    A message renderer is responsible for taking one, or more, templates,
    and context, and outputting a rendered message for a specific message
    channel (e.g. email, SMS, push notification).
    """
    rendered_message_cls = None

    def render(self, channel, message):
        u"""
        Renders the given message.

        Args:
             channel (:class:`Channel`): The channel to render the message for.
             message (:class:`Message`): The message being rendered.

         Returns:
             dict: Mapping of template names/types to rendered text.
        """
        rendered = {}
        for attribute in attr.fields(self.rendered_message_cls):
            # TODO(later): Add comments to explain this difference in
            # behavior between html and txt files, or make it consistent.
            field = attribute.name
            if field.endswith(u'_html'):
                filename = field.replace(u'_html', u'.html')
            else:
                filename = field + u'.txt'
            template = self.get_template_for_message(channel, message, filename)
            render_context = {
                u'message': message,
                u'channel': channel,
            }
            render_context.update(message.context)
            rendered[field] = template.render(render_context)

        return self.rendered_message_cls(**rendered)  # pylint: disable=not-callable

    def get_template_for_message(self, channel, message, filename):
        u"""
        Arguments:
            message (:class:`Message`): The message being rendered.
            filename (str): The basename of the template file to look up.

        Returns:
            The full template path to the template to render.
        """
        template_path = u'{app_label}/edx_ace/{name}/{channel_type}/{filename}'.format(
            app_label=message.app_label,
            name=message.name,
            channel_type=channel.channel_type.value,
            filename=filename,
        )
        return loader.get_template(template_path)


@attr.s
class RenderedEmail(object):
    u"""
    Encapsulates all values needed to send a :class:`.Message`
    over an :attr:`.ChannelType.EMAIL`.
    """
    from_name = attr.ib()
    subject = attr.ib()
    body_html = attr.ib()
    head_html = attr.ib()
    body = attr.ib()


class EmailRenderer(AbstractRenderer):
    u"""
    A renderer for :attr:`.ChannelType.EMAIL` channels.
    """
    rendered_message_cls = RenderedEmail
