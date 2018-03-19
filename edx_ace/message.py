# -*- coding: utf-8 -*-
u"""
:mod:`edx_ace.message` contains the core :class:`Message` and :class:`MessageType`
classes, which allow specification of the content to be delivered by ACE.
"""
from __future__ import absolute_import, division, print_function

import logging
from abc import ABCMeta
from uuid import UUID, uuid4

import attr
import six

from django.apps import apps

import edx_ace.utils.date as date
from edx_ace.monitoring import report as monitoring_report
from edx_ace.recipient import Recipient
from edx_ace.serialization import MessageAttributeSerializationMixin


@attr.s
@six.add_metaclass(ABCMeta)
class Message(MessageAttributeSerializationMixin):
    u"""
    A ``Message`` is the core piece of data that is passed into ACE.
    It captures the message, recipient, and all context needed to render
    the message for delivery.

    Arguments:
        app_label (str): The name of the Django app that is sending
            this message. Used to look up the appropriate template
            during rendering. Required.
        name (str): The name of this type of message. Used to look up
            the appropriate template during rendering. Required.

        recipient (:class:`.Recipient`): The intended recipient of the
            message. Optional.
        expiration_time(:class:`~datetime.datetime`): The date and time
            at which this message expires. After this time, the message
            should not be delivered. Optional.
        context (dict): A dictionary to be supplied to the template at
            render time as the context.
        send_uuid (:class:`uuid.UUID`): The :class:`uuid.UUID` assigned
            to this bulk-send of many messages.
        language (str): The language the message should be rendered in.
            Optional.
    """

    # mandatory attributes
    # Name is the unique identifier for the message type.
    # Used for:
    #   tracking
    #   discovering message presentation templates
    app_label = attr.ib()
    name = attr.ib()

    # optional attributes
    recipient = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(Recipient)),
    )

    expiration_time = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(date.datetime)),
    )

    context = attr.ib()

    # TODO(later): better naming to distinguish between these 2 UUIDs
    uuid = attr.ib(
        init=False,
        validator=attr.validators.instance_of(UUID),
    )
    send_uuid = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(UUID)),
        default=None
    )
    options = attr.ib()
    language = attr.ib(default=None)
    log_level = attr.ib(default=None)

    @context.default
    def default_context_value(self):
        return {}

    @options.default
    def default_options_value(self):
        return {}

    @uuid.default
    def generate_uuid(self):
        return uuid4()

    @property
    def unique_name(self):
        u"""
        A unique name for this message, used for logging and reporting.

        Returns: str
        """
        return u'.'.join([self.app_label, self.name])

    @property
    def log_id(self):
        u"""
        The identity of this message for logging.
        """
        return u'.'.join([
            self.unique_name,
            six.text_type(self.send_uuid) if self.send_uuid else u'no_send_uuid',
            six.text_type(self.uuid)
        ])

    def get_message_specific_logger(self, logger):
        u"""
        Arguments:
            logger (:class:`logging.Logger`): The logger to be adapted.

        Returns:  :class:`.MessageLoggingAdapter` that is specific to this message.
        """
        return MessageLoggingAdapter(logger, {u'message': self})

    def report_basics(self):
        monitoring_report(u'message_name', self.unique_name)
        monitoring_report(u'language', self.language)

    def report(self, key, value):
        monitoring_report(key, value)


class MessageLoggingAdapter(logging.LoggerAdapter):
    u"""
    A :class:`logging.LoggingAdapter` that prefixes log items with
    a message :attr:`.log_id`.ABCMeta

    Expects a ``message`` key in its ``extra`` argument which should
    contain the :class:`.Message` being logged for.
    """
    def process(self, msg, kwargs):
        return u'[%s] %s' % (self.extra[u'message'].log_id, msg), kwargs

    def debug(self, msg, *args, **kwargs):
        log_level = self.extra[u'message'].log_level
        if log_level and log_level <= logging.DEBUG:
            return self.info(msg, *args, **kwargs)
        else:
            super(MessageLoggingAdapter, self).debug(msg, *args, **kwargs)


@attr.s(cmp=False)
class MessageType(MessageAttributeSerializationMixin):
    u"""
    A class representing a type of :class:`Message`. An instance of
    a ``MessageType`` is used for each batch send of messages.

    Arguments:
        context (dict): Context to be supplied to all messages sent in
            this batch of messages.
        expiration_time (:class:`datetime.datetime`): The time at which
            these messages expire.
        app_label (str): Override the Django app that is used to resolve
            the template for rendering. Defaults to :attr:`.APP_LABEL` or
            to the app that the message type was defined in.
        name (str): Override the message name that is used to resolve
            the template for rendering. Defaults to :attr:`.NAME` or
            to the name of the class.
    """
    NAME = None
    APP_LABEL = None

    context = attr.ib()
    uuid = attr.ib(
        init=False,
        validator=attr.validators.instance_of(UUID),
    )
    expiration_time = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(date.datetime)),
    )
    app_label = attr.ib()
    name = attr.ib()
    options = attr.ib()
    log_level = attr.ib(default=None)

    @context.default
    def default_context_value(self):
        return {}

    @options.default
    def default_options_value(self):
        return {}  # pragma: no cover

    @uuid.default
    def generate_uuid(self):
        return uuid4()

    @name.default
    def default_name(self):
        if self.NAME is None:
            return self.__class__.__name__.lower()
        else:
            return self.NAME

    @app_label.default
    def default_app_label(self):
        if self.APP_LABEL is None:
            return apps.get_containing_app_config(self.__class__.__module__).label
        else:
            return self.APP_LABEL

    def personalize(self, recipient, language, user_context):
        u"""
        Personalize this `MessageType` to a specific recipient, in order to
        send a specific message.

        Arguments:
            recipient (:class:`.Recipient`): The intended recipient of the
                message. Optional.
            language (str): The language the message should be rendered in.
                Optional.
            user_context (dict): A dictionary containing recipient-specific
                context to be supplied to the template at render time.

        Returns: A new :class:`.Message` that has been personalized to a
            specific recipient.
        """
        context = dict(self.context)
        context.update(user_context)
        return Message(
            app_label=self.app_label,
            name=self.name,
            expiration_time=self.expiration_time,
            context=context,
            send_uuid=self.uuid,
            recipient=recipient,
            language=language,
            log_level=self.log_level,
            options=self.options,
        )

    # We override these so that a subtype of MessageType can compare equal
    # to a deserialized non-subtyped MessageType
    def __eq__(self, other):
        if isinstance(other, MessageType):
            return attr.astuple(self) == attr.astuple(other)
        else:
            return NotImplemented

    def __hash__(self):
        return hash(attr.astuple(self))

    def __ne__(self, other):
        result = self == other
        if result == NotImplemented:
            return NotImplemented
        else:
            return not result
