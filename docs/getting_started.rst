Getting Started
===============

If you have not already done so, create/activate a `virtualenv`_. Unless otherwise stated, assume all terminal code
below is executed within the virtualenv.

.. _virtualenv: https://virtualenvwrapper.readthedocs.org/en/latest/


Install dependencies
--------------------
Dependencies can be installed via the command below.

.. code-block:: bash

    $ make requirements


Configure delivery channels
---------------------------

Certain delivery channels may require additional configuration
before they will function correctly.

:class:`~.SailthruEmailChannel` Settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: /../edx_ace/channel/sailthru.py
    :start-after: .. settings_start
    :end-before: .. settings_end
    :language: python
    :dedent: 12

:class:`~.DjangoEmailChannel` Settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: /../edx_ace/channel/django_email.py
    :start-after: .. settings_start
    :end-before: .. settings_end
    :language: python
    :dedent: 12

Create a message
----------------

Each message sent with ACE is represented by an instance of :class:`.Message`.
These can be created manually, or can be created by calling :meth:`.MessageType.personalize`
on a :class:`.MessageType` instance. The name and package of the :class:`.MessageType`
determines what templates will be used when the :class:`.Message` is rendered for delivery.

For example, the class

.. code:: python

    # myapp/messages.py

    class CustomMessage(edx_ace.message.MessageType):
        pass

would use the following templates when rendered for email delivery:

.. code::

    myapp/edx_ace/custommessage/email/from_name.txt
    myapp/edx_ace/custommessage/email/subject.txt
    myapp/edx_ace/custommessage/email/body.html
    myapp/edx_ace/custommessage/email/head.html
    myapp/edx_ace/custommessage/email/body.txt

These all follow the format ``{app_label}/edx_ace/{message_name}/{renderer}/{attribute}``,
where the ``app_label`` and ``message_name`` are defined by the :class:`.MessageType` (or
the manually created :class:`.Message`), and ``renderer`` and ``attribute`` come from
the renderer being used by the specific delivery channel. The templates will be retrieved
using standard Django template resolution mechanisms.

The specific templates needed for existing renderers are listed in :py:mod:`edx_ace.renderers`.

Transactional messages
----------------------

Transactional messages such as password reset should be marked as ``options.transactional = True``,
to ensure that it won't be subject to marketing messages opt-out policies.
While not required, transactional messages are recommended to use the ``django_email`` channel which supports
a custom ``options.from_address`` email. For example:

.. code:: python

    # myapp/messages.py

    class PurchaseOrderComplete(edx_ace.message.MessageType):
        def __init__(self, *args, **kwargs):
            super(PurchaseOrderComplete, self).__init__(*args, **kwargs)

            self.options['transactional'] = True
            self.options['from_address'] = settings.ECOMMERCE_FROM_EMAIL

Send a message
--------------

The simplest way to send a message using ACE is to just create it, and call :py:func:`edx_ace.ace.send`.

.. code-block:: python

    from edx_ace import ace
    from edx_ace.messages import Message

    msg = Message(
        name="test_message",
        app_label="my_app",
        recipient=Recipient(username='a_user', email='a_user@example.com'),
        language='en',
        context={
            'stuff': 'to personalize the message',
        }
    )
    ace.send(msg)

The ``name`` and ``app_label`` attributes are required in order for ACE to look
up the correct templates in the Django environment.

For messages being sent from multiple places in the code, it can be simpler to
define a :class:`.MessageType` first, and then :meth:`.MessageType.personalize` it.

.. code-block:: python

    from edx_ace import ace
    from edx_ace.messages import Message

    class TestMessage(MessageType):
        APP_LABEL = "my_app"  # Optional
        NAME = "test_message"  # Optional

    msg_type = TestMessage(
        context={
            'generic_stuff': 'that is applicable to all recipients'
        }
    )

    for recipient in recipients:
        msg = msg_type.personalize(
            recipient=recipient,
            language='en',
            context={
                'stuff': 'to personalize the message',
            }
        )
        ace.send(msg)
