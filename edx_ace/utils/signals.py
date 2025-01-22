"""
Utils for signals.
"""
from django.utils import translation
from edx_ace.signals import ACE_MESSAGE_SENT


def make_serializable_object(obj):
    """
    Takes a dictionary/list and returns a dictionary/list with all the values converted
    to JSON serializable objects.
    """
    try:
        if isinstance(obj, (int, float, str, bool)) or obj is None:
            return obj
        elif isinstance(obj, dict):
            return {key: make_serializable_object(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [make_serializable_object(element) for element in obj]
    except Exception:    # pylint: disable=broad-except
        pass
    return str(obj)


def send_ace_message_sent_signal(channel, message):
    """
    Creates dictionary from message, makes it JSON serializable and
    sends the ACE_MESSAGE_SENT signal.
    """
    try:
        channel_name = channel.__class__.__name__
    except AttributeError:
        channel_name = 'Other'
    data = {
        'name': message.name,
        'app_label': message.app_label,
        'recipient': {
            'email': getattr(message.recipient, 'email_address', ''),
            'user_id': getattr(message.recipient, 'lms_user_id', ''),
        },
        'channel': channel_name,
        'context': message.context,
        'options': message.options,
        'uuid': str(message.uuid),
        'send_uuid': str(message.send_uuid),
        'message_language': message.language,
        'translation_language': translation.get_language()
    }
    ACE_MESSAGE_SENT.send(sender=channel, message=make_serializable_object(data))
