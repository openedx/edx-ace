from unittest import TestCase
from edx_ace.recipient import Recipient
from edx_ace.message import Message
from edx_ace.utils.date import get_current_time


class TestMessageTemplate(TestCase):
    def setUp(self):
        self.msg_kwargs = {
            'app_label': u'test_app_label',
            'name': u'test_message',
            'expiration_time': get_current_time(),
            'context': {
                u'key1': u'value1',
                u'key2': u'value2',
            },
            'recipient': Recipient(
                username=u'me',
                fields={
                    u'key3': u'value3',
                }
            )
        }

    def test_basic(self):
        msg = Message(**self.msg_kwargs)
        for key in self.msg_kwargs:
            self.assertEquals(getattr(msg, key), self.msg_kwargs.get(key))
        self.assertIsNotNone(msg.uuid)

    def test_serialization(self):
        msg = Message(**self.msg_kwargs)
        string_value = unicode(msg)
        resurrected_msg = Message.from_string(string_value)
        self.assertEquals(repr(msg), repr(resurrected_msg))
