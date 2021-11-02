'''
edx-ace template tags
'''
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def get_action_links(context, channel, omit_unsubscribe_link=False):
    """
    Retrieve the action links for the channel and pass the omit_unsubscribe_link argument
    """
    if getattr(channel, 'get_action_links', None):
        return channel.get_action_links(omit_unsubscribe_link=context.get('omit_unsubscribe_link'))
    return []
