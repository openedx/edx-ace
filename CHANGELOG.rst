Change Log
----------

..
   All enhancements and patches to edx_ace will be documented
   in this file.  It adheres to the structure of http://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (http://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
~~~~~~~~~~

[1.4.0] - 2021-11-08
~~~~~~~~~~~~~~~~~~~~

* Deprecate the action_links property
* Add a get_action_links method and template tag to allow passing arguments to action links

[1.3.1] - 2021-08-17
~~~~~~~~~~~~~~~~~~~~

* Adjust name ``handles_delivery_for_message`` to ``overrides_delivery_for_message``

[1.3.0] - 2021-08-16
~~~~~~~~~~~~~~~~~~~~

* New channel method ``handles_delivery_for_message`` for allowing a default channel
  to claim a message, even if it would normally be delivered to the configured
  transactional channel.
* Braze: Will handle any message defined in ``ACE_CHANNEL_BRAZE_CAMPAIGNS`` (using the
  above new feature) to steal campaign messages from the transactional channel as
  needed.

[1.2.0] - 2021-07-16
~~~~~~~~~~~~~~~~~~~~

* Added support for django 3.2

[1.1.1] - 2021-07-09
~~~~~~~~~~~~~~~~~~~~

* Removed upper constraint from Django

[1.1.0] - 2021-03-26
~~~~~~~~~~~~~~~~~~~~

* Braze: Add ACE_CHANNEL_BRAZE_FROM_EMAIL setting to override the normal from address
* Sailthru: Remove Braze rollout waffle flag

[1.0.1] - 2021-03-15
~~~~~~~~~~~~~~~~~~~~

* Braze: Add an unsubscribe action link
* Braze: Don't ask Braze to inline css, as ACE templates already have inline css

[1.0.0] - 2021-03-11
~~~~~~~~~~~~~~~~~~~~

* BREAKING: Recipient objects now take `lms_user_id` instead of `username`
* New `braze_email` backend, needing the following new configuration:

  * ACE_CHANNEL_BRAZE_API_KEY
  * ACE_CHANNEL_BRAZE_APP_ID
  * ACE_CHANNEL_BRAZE_REST_ENDPOINT (like `rest.iad-01.braze.com`)
  * ACE_CHANNEL_BRAZE_CAMPAIGNS (an optional dictionary of ACE message names to Braze campaign identifiers)

[0.1.18] - 2020-11-19
~~~~~~~~~~~~~~~~~~~~~

* Updated he travis-badge in README.rst to point to travis-ci.com

[0.1.17] - 2020-10-19
~~~~~~~~~~~~~~~~~~~~~

* Use IntEnum to avoid silent failure in value comparisons

[0.1.16] - 2020-10-17
~~~~~~~~~~~~~~~~~~~~~

* Fixed Enum usage for Python 3.8 to avoid TypeError when comparing values

[0.1.15] - 2020-03-11
~~~~~~~~~~~~~~~~~~~~~

* Added support for Python 3.8
* Removed support for Django 2.0 and 2.1

[0.1.14] - 2020-03-11
~~~~~~~~~~~~~~~~~~~~~

* Fix trivial warning from deprecated use of attr library.

[0.1.13] - 2019-12-06
~~~~~~~~~~~~~~~~~~~~~

* Django22 Support.

[0.1.12] - 2019-10-16
~~~~~~~~~~~~~~~~~~~~~

* Reply_to field added in emails.

[0.1.10] - 2018-11-01
~~~~~~~~~~~~~~~~~~~~~

* Django lazy text translations are handled properly.


[0.1.9] - 2018-07-13
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Updated delivery logging


[0.1.0] - 2017-08-08
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Added
_____

* First release on PyPI.
