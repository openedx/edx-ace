from unittest import TestCase
from edx_ace.message import Message, MessageTemplate, MessageBase
from edx_ace.utils.date import get_current_time


class TestMessageTemplate(TestCase):
    def setUp(self):
        self.msg_kwargs = {
            'name': u'test_message',
            'expiration_time': get_current_time(),
            'fields': {
                'key1': u'value1',
                'key2': u'value2',
            },
        }

    def test_basic(self):
        msg = MessageTemplate.create(**self.msg_kwargs)
        for key in self.msg_kwargs:
            self.assertEquals(getattr(msg, key), self.msg_kwargs.get(key))
        self.assertIsNotNone(msg.uuid)

    def test_to_from_json(self):
        msg = MessageTemplate.create(**self.msg_kwargs)
        json_value = msg.to_json()
        resurrected_msg = MessageBase.from_json(json_value)
        self.assertEquals(repr(msg), repr(resurrected_msg))

    def test_to_from_string(self):
        msg = MessageTemplate.create(**self.msg_kwargs)
        string_value = unicode(msg)
        resurrected_msg = MessageBase.from_string(string_value)
        self.assertEquals(repr(msg), repr(resurrected_msg))
