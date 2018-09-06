.. edx-ace documentation master file, created by
   sphinx-quickstart on Tue Aug 08 16:13:14 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

edX Automated Communication Engine (A.C.E.)
===========================================

The Automated Communication Engine, ACE for short, is a Django app for
messaging learners on the edX platform. This app can be installed in any Open
edX project, but has only been tested with ``edx-platform``. Email delivery
(via Sailthru or Django email) is the only current delivery channel. In the
future we may add support for other delivery channels such as push
notifications.


.. toctree::
   :maxdepth: 2

   getting_started
   design
   testing
   modules
   changelog


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
