# lint-amnesty, pylint: disable=missing-docstring
import attr
from django.template import loader
from edx_ace.channel import ChannelType


class AbstractRenderer(object):
    """
    Base class for message renderers.

    A message renderer is responsible for taking one, or more, templates,
    and context, and outputting a rendered message for a specific message
    channel (e.g. email, SMS, push notification).
    """
    channel = None
    rendered_message_cls = None

    def render(self, message):
        """
        Renders the given message.

        Args:
             message (Message)

         Returns:
             dict: Mapping of template names/types to rendered text.
        """
        rendered = {}
        for attribute in attr.fields(self.rendered_message_cls):
            # TODO(later): Add comments to explain this difference in
            # behavior between html and txt files, or make it consistent.
            field = attribute.name
            if field.endswith('_html'):
                filename = field.replace('_html', '.html')
            else:
                filename = field + '.txt'
            template = self.get_template_for_message(message, filename)
            rendered[field] = template.render(message.context)

        return self.rendered_message_cls(**rendered)  # lint-amnesty, pylint: disable=not-callable

    def get_template_for_message(self, message, filename):  # lint-amnesty, pylint: disable=missing-docstring
        template_path = "{msg.app_label}/edx_ace/{msg.name}/{channel.value}/{filename}".format(  # lint-amnesty, pylint: disable=missing-format-attribute
            msg=message,
            channel=self.channel,
            filename=filename,
        )
        return loader.get_template(template_path)


@attr.s  # lint-amnesty, pylint: disable=missing-docstring
class RenderedEmail(object):
    from_name = attr.ib()
    subject = attr.ib()
    body_html = attr.ib()
    head_html = attr.ib()
    body = attr.ib()


class EmailRenderer(AbstractRenderer):
    channel = ChannelType.EMAIL
    rendered_message_cls = RenderedEmail
