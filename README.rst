edX Automated Communication Engine (A.C.E.)
###########################################

|License: AGPL v3| |Python CI| |Publish package to PyPi| |Status| |pypi-badge| |travis-badge| |codecov-badge|
|doc-badge| |pyversions-badge|

Purpose
=======

The `automated communication engine <https://edx-ace.readthedocs.io/en/latest/>`_, A.C.E. for short, is a Django app
for messaging learners on the Open edX platform. This
app can be installed in any Open edX project, but has only been tested with ``edx-platform``. Email delivery
(via Sailthru and Django Email)
are the currently supported delivery channels. In the future we may add support for other delivery channels such as push
notifications.

Getting Started
===============

For instructions on starting local development, see `Getting Started <https://github.com/openedx/edx-ace/blob/master/docs/getting_started.rst>`_.

Getting Help
============

Documentation
-------------

See `the documentation`_.  If you need more help see below.

.. _the documentation: https://edx-ace.readthedocs.io/en/latest/

More Help
----------

If you're having trouble, we have discussion forums at
https://discuss.openedx.org where you can connect with others in the
community.

Our real-time conversations are on Slack. You can request a `Slack
invitation`_, then join our `community Slack workspace`_.

For anything non-trivial, the best path is to open an issue in this
repository with as many details about the issue you are facing as you
can provide.

https://github.com/openedx/edx-ace/issues

For more information about these options, see the `Getting Help`_ page.

.. _Slack invitation: https://openedx.org/slack
.. _community Slack workspace: https://openedx.slack.com/
.. _Getting Help: https://openedx.org/getting-help

License
=======

The code in this repository is licensed under the AGPL 3.0 unless
otherwise noted.

Please see ``LICENSE.txt`` for details.

Contributing
============

Contributions are very welcome.

Please read `How To Contribute <https://openedx.org/r/how-to-contribute>`_ for details.

Even though they were written with ``edx-platform`` in mind, the guidelines
should be followed for Open edX code in general.

PR description template should be automatically applied if you are sending PR from github interface; otherwise you
can find it
at `PULL_REQUEST_TEMPLATE.md <https://github.com/openedx/edx-ace/blob/master/.github/PULL_REQUEST_TEMPLATE.md>`_

Issue report template should be automatically applied if you are sending it from github UI as well; otherwise you
can find it at `ISSUE_TEMPLATE.md <https://github.com/openedx/edx-ace/blob/master/.github/ISSUE_TEMPLATE.md>`_

The Open edX Code of Conduct
============================

All community members are expected to follow the `Open edX Code of Conduct`_.

.. _Open edX Code of Conduct: https://openedx.org/code-of-conduct/

People
======

The assigned maintainers for this component and other project details may be
found in `Backstage`_. Backstage pulls this data from the ``catalog-info.yaml``
file in this repo.

.. _Backstage: https://open-edx-backstage.herokuapp.com/catalog/default/component/edx-ace

Reporting Security Issues
=========================

Please do not report security issues in public. Please email security@openedx.org.

.. |pypi-badge| image:: https://img.shields.io/pypi/v/edx-ace.svg
    :target: https://pypi.python.org/pypi/edx-ace/
    :alt: PyPI

.. |travis-badge| image:: https://travis-ci.com/edx/edx-ace.svg?branch=master
    :target: https://travis-ci.com/edx/edx-ace
    :alt: Travis

.. |codecov-badge| image:: http://codecov.io/github/edx/edx-ace/coverage.svg?branch=master
    :target: http://codecov.io/github/edx/edx-ace?branch=master
    :alt: Codecov

.. |doc-badge| image:: https://readthedocs.org/projects/edx-ace/badge/?version=latest
    :target: http://edx-ace.readthedocs.io/en/latest/
    :alt: Documentation

.. |pyversions-badge| image:: https://img.shields.io/pypi/pyversions/edx-ace.svg
    :target: https://pypi.python.org/pypi/edx-ace/
    :alt: Supported Python versions

.. |license-badge| image:: https://img.shields.io/github/license/edx/edx-ace.svg
    :target: https://github.com/openedx/edx-ace/blob/master/LICENSE.txt
    :alt: License

.. |License: AGPL v3| image:: https://img.shields.io/badge/License-AGPL_v3-blue.svg
  :target: https://www.gnu.org/licenses/agpl-3.0

.. |Python CI| image:: https://github.com/openedx/edx-ace/actions/workflows/ci.yml/badge.svg
  :target: https://github.com/openedx/edx-ace/actions/workflows/ci.yml

.. |Publish package to PyPi| image:: https://github.com/openedx/edx-ace/actions/workflows/pypi-publish.yml/badge.svg
  :target: https://github.com/openedx/edx-ace/actions/workflows/pypi-release.yml

.. |Status| image:: https://img.shields.io/badge/Status-Maintained-brightgreen
