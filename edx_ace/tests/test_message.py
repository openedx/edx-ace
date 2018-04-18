u"""
Tests of :mod:`edx_ace.message`.
"""
from __future__ import absolute_import

import logging
from functools import partial
from unittest import TestCase

import ddt
import six
from hypothesis import given
from hypothesis import strategies as st
from hypothesis.extra.pytz import timezones
from mock import patch

from edx_ace.message import Message, MessageType
from edx_ace.recipient import Recipient
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
        username=st.text(),
    ),
    send_uuid=st.one_of(st.uuids(), st.none()),
)


@ddt.ddt
class TestMessage(TestCase):
    u"""
    Tests of :class:`.Message` and :class:`.MessageType`.
    """
    def setUp(self):
        self.msg_kwargs = {
            u'app_label': u'test_app_label',
            u'name': u'test_message',
            u'expiration_time': get_current_time(),
            u'context': {
                u'key1': u'value1',
                u'key2': u'value2',
            },
            u'recipient': Recipient(
                username=u'me',
            )
        }

    def test_basic(self):
        transactional_message = Message(options={u'transactional': True}, **self.msg_kwargs)
        for key in self.msg_kwargs:
            self.assertEqual(getattr(transactional_message, key), self.msg_kwargs.get(key))
        self.assertIsNotNone(transactional_message.uuid)
        assert transactional_message.options.get(u'transactional')  # pylint: disable=no-member

        normal_message = Message(**self.msg_kwargs)
        assert not dict(normal_message.options)

    def test_serialization(self):
        message = Message(**self.msg_kwargs)
        string_value = six.text_type(message)
        resurrected_msg = Message.from_string(string_value)
        self.assertEqual(message, resurrected_msg)

    @given(msg)
    def test_serialization_round_trip(self, message):
        serialized = six.text_type(message)
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

        self.msg_kwargs[u'log_level'] = log_level
        message = Message(**self.msg_kwargs)
        logger = message.get_message_specific_logger(LOG)
        with patch(u'logging.Logger.callHandlers') as mock_log:
            logger.warning(u'Test warning statement')
            self.assertEqual(mock_log.called, expect_log_warn)
        with patch(u'logging.Logger.callHandlers') as mock_log:
            logger.debug(u'Test debug statement')
            self.assertEqual(mock_log.called, expect_log_debug)


def mk_message_type(name, app_label):
    u"""
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
    @given(msg_type)
    def test_serialization_roundtrip(self, message_type):
        serialized = six.text_type(message_type)
        parsed = MessageType.from_string(serialized)
        self.assertEqual(message_type, parsed)
