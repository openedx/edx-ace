"""
Tests of :mod:`edx_ace.message`.
"""
import logging
from functools import partial
from unittest import TestCase
from unittest.mock import patch

import ddt
from hypothesis import given
from hypothesis import strategies as st
from hypothesis.extra.pytz import timezones

from django.utils.translation import ugettext_lazy

from edx_ace.message import Message, MessageType
from edx_ace.recipient import Recipient
from edx_ace.serialization import MessageEncoder
from edx_ace.utils.date import get_current_time

LOG = logging.getLogger(__name__)

context_values = st.one_of(st.text(), st.booleans(), st.floats(allow_nan=False))
dates = st.datetimes(timezones=st.none() | timezones() | st.none())

msg = st.builds(
    Message,
    app_label=st.text(),
    name=st.text(),
    expiration_time=dates,
    context=st.dictionaries(
        st.text(),
        context_values,
    ),
    recipient=st.builds(
        Recipient,
        lms_user_id=st.integers(min_value=1),
    ),
    send_uuid=st.one_of(st.uuids(), st.none()),
)


@ddt.ddt
class TestMessage(TestCase):
    """
    Tests of :class:`.Message` and :class:`.MessageType`.
    """
    def setUp(self):
        super().setUp()
        self.msg_kwargs = {
            'app_label': 'test_app_label',
            'name': 'test_message',
            'expiration_time': get_current_time(),
            'context': {
                'key1': 'value1',
                'key2': 'value2',
            },
            'recipient': Recipient(
                lms_user_id=123,
            )
        }

        self.encoder = MessageEncoder()

    def test_basic(self):
        transactional_message = Message(options={'transactional': True}, **self.msg_kwargs)
        for key in self.msg_kwargs:
            self.assertEqual(getattr(transactional_message, key), self.msg_kwargs.get(key))
        self.assertIsNotNone(transactional_message.uuid)
        assert transactional_message.options.get('transactional')

        normal_message = Message(**self.msg_kwargs)
        assert not dict(normal_message.options)

    def test_serialization(self):
        message = Message(**self.msg_kwargs)
        string_value = str(message)
        resurrected_msg = Message.from_string(string_value)
        self.assertEqual(message, resurrected_msg)

    def test_serialization_lazy_text(self):
        unicode_text = "A 𝓾𝓷𝓲𝓬𝓸𝓭𝓮 Text"
        lazy_text = ugettext_lazy(unicode_text)                    # pylint: disable=translation-of-non-string
        self.assertEqual(self.encoder.default(lazy_text), unicode_text)

    @given(msg)
    def test_serialization_round_trip(self, message):
        serialized = str(message)
        parsed = Message.from_string(serialized)
        self.assertEqual(message, parsed)

    @ddt.data(
        (None, True, False),
        (logging.WARNING, True, False),
        (logging.DEBUG, True, True),
    )
    @ddt.unpack
    def test_log_level(self, log_level, expect_log_warn, expect_log_debug):
        logging.getLogger().setLevel(logging.INFO)

        self.msg_kwargs['log_level'] = log_level
        message = Message(**self.msg_kwargs)
        logger = message.get_message_specific_logger(LOG)
        with patch('logging.Logger.callHandlers') as mock_log:
            logger.warning('Test warning statement')
            self.assertEqual(mock_log.called, expect_log_warn)
        with patch('logging.Logger.callHandlers') as mock_log:
            logger.debug('Test debug statement')
            self.assertEqual(mock_log.called, expect_log_debug)


def mk_message_type(name, app_label):
    """
    Create a new :class:`MessageType` subclass for testing purposes.

    Arguments:
        name: The NAME class attribute to set.
        app_label: The APP_LABEL class attribute to set.
    """
    class CustomType(MessageType):
        NAME = name
        APP_LABEL = app_label

    return CustomType


msg_type = st.builds(
    mk_message_type,
    name=st.one_of(st.none(), st.text()),
    app_label=st.text(),
).flatmap(
    partial(
        st.builds,
        expiration_time=dates,
        context=st.dictionaries(
            st.text(),
            context_values,
        ),
    )
)


class TestMessageTypes(TestCase):
    """ Test Message Types. """
    @given(msg_type)
    def test_serialization_roundtrip(self, message_type):
        serialized = str(message_type)
        parsed = MessageType.from_string(serialized)
        self.assertEqual(message_type, parsed)
