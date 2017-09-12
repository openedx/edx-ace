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
Each delivery channel requires its own configuration via Django settings.

Sailthru
~~~~~~~~
`Sailthru <http://www.sailthru.com/>`_ is an email delivery channel. All settings below are required. The API key and
secret can be retrieved from https://my.sailthru.com/settings/api_postbacks.

.. list-table::
   :widths: auto
   :header-rows: 1

   * - Setting
     - Description
   * - ``ACE_CHANNEL_SAILTHRU_API_KEY``
     - API key used to send an email via the `send API endpoint <https://getstarted.sailthru.com/developers/api/send/>`_
   * - ``ACE_CHANNEL_SAILTHRU_API_SECRET``
     - API secret used to send an email via the `send API endpoint <https://getstarted.sailthru.com/developers/api/send/>`_
   * - ``ACE_CHANNEL_SAILTHRU_TEMPLATE_NAME``
     - Base template for all messages


Create a message
----------------
TODO: List template files that need to be present


Send a message
--------------
TODO: Add message

.. code-block:: python

    from edx_ace import ace

    msg = ...
    ace.send(msg)
