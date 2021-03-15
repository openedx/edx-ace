Allow for In-Braze Message Templating
=====================================

Status
------

Draft

Context
-------

With the existing ACE channels, Marketing (edX's marketing team) can't directly manage the
content of the emails being sent. In order to enhance their ability to improve edX's
marketing content, we (edX Engineering) want to expose the contents and performance of
the marketing flows that are powered by ACE to that team.

When exposing those data to Marketing, and allowing them to make changes
to improve the content, we would like to make sure that they aren't blocked by the engineering
organization. However, we also need to be mindful of existing open-source uses of ACE as
well, and that we don't lose the ability to maintain those uses.

While looking at Braze functionality, it was determined that there isn't a good way for us
to schedule campaigns with flexible dates based on single events. This is a feature we were
looking to use to allow Marketing to handle dynamic pacing email (or schedule-based
campaigns). However, because of current restrictions in the Braze platform, this is likely
not possible.

Decision
--------

We will use existing ACE emails to trigger events in Braze, and then allow Marketing
to send campaigns based on those ACE email events. These events will be sent whenever
an email is sent by the Braze channel in ACE, directly using the Braze event API
(https://www.braze.com/docs/api/endpoints/user_data/post_user_track/). They will include
all the properties currently used to template into the ACE Django templates, and will be
named based on the name of the ACE email being sent.

We will also add the ability to disable specific Braze-channel emails from being sent via
the API, so that we can control which emails will be sent via event trigger Braze campaigns,
and which will be sent via the direct email API.
