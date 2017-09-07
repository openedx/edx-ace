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
TODO: List settings that need to be setup


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
