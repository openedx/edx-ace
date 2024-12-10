Implement Push Notification Channel
===================================

Status
--------

Accepted

Context
--------

The goal of ACE framework is to provide extensible mechanism for extending delivery channels and policies.
However, as of June 2024, edx-ace supports various email delivery channels like
django and Sailthru as well as third party API integration for Braze, but lacks
support for direct mobile push notifications.
Adding push notifications delivery channel will enable real-time communication
with users through their mobile devices, enhancing user engagement and
ensuring timely delivery of important information.
Flexibility and seamless integration with the existing framework are priorities for this new notification channel.

`ace.send` already supports sending via multiple channels, so in order to send both push and email notifications,
it's required to add a new channel specifically for mobile push notifications to edx-ace.

Decision
--------

It was decided to implement a new mobile push notifications channel in edx-ace.
Data for push notifications must be formatted according to mobile push notification requirements.
It should be possible to add optional payloads for advanced functionality,
e.g., data to build depplink to specific mobile screen.
The formatted push notification should be sent using the firebase_admin_ SDK to Firebase Cloud Messaging service
which will redistribute it to the user's mobile devices.

It was decided not to expand the codebase unnecessarily and to not implement from scratch
models for storing user device tokens, mechanisms for sending push notifications,
or mechanisms for deactivating inactive tokens. All of this functionality is available
and will be provided using the django-push-notifications_ package.
Therefore, it is better for edx-ace to use the existing `GCMDevice` model,
and on the edx-platform side, add the `GCMDeviceViewSet` view to allow mobile
devices to send their tokens.

It is proposed to add a new optional argument `limit_to_channels=None` to the
`ace.send` method, by using it is possible to specify the list of channels through which
messages should be sent. This approach will give us a lot of flexibility,
for example in case with discussion notifications we need to send
a mobile push notification on each new reply to the forum post,
while an email is sent only for the first reply to a post.

With the use of `limit_to_channels` argument the code to send a message using `ace` may look like this:

.. code-block:: python

    message_context = _build_message_context(context, notification_type='forum_response')
    message = ResponseNotification().personalize(
        Recipient(thread_author.id, thread_author.email),
        _get_course_language(context['course_id']),
        message_context
    )
    log.info('Sending forum comment notification with context %s', message_context)
    if _is_first_comment(context['comment_id'], context['thread_id']):
        limit_to_channels = None
    else:
        limit_to_channels = [ChannelType.PUSH]
    ace.send(message, limit_to_channels=limit_to_channels)


For the first response, as it is currently implemented in edx-platform, the message is sent
to all configured ace channels, but for all following replies only mobile push notifications are sent.

In order to allow advanced functionality on mobile, for example deeplinking to the specific forum post,
the `_build_message_context` method should be extended with the extra context:

.. code-block:: python

    'push_notification_extra_context': {
        'notification_type': 'notification_type',
        'thread_id': context['thread_id'],
        'comment_id': context['comment_id'],
    }


The presence of `push_notification_extra_context` will be checked in the
`CoursePushNotificationOptout`, and based on the output it will be determined
whether a message can be sent to `PushNotificationChannel`.

It should also be noted that django-push-notifications_ does not currently
implement sending notifications to IOS devices using the FCM channel,
although the FCM service itself supports it.
Therefore it was decided to add support for IOS devices on the edx-ace side.
An additional method will be added to `PushNotificationChannel`, this method implements
the collection of the necessary context parameters for iOS devices to send
a push notification using FCM service.
In the future this change will be contributed to the django-push-notifications_ package.

The implementation of all decisions listed above involve:
  - PushNotificationRenderer: Responsible for formatting and structuring the content
    of a push notification. This includes setting the notification's title, body,
    and optional data payload. The renderer will ensure that the notification content
    adheres to the specifications required by the firebase_admin_ SDK.
  - PushNotificationChannel: Handles sending formatted push notifications using
    the firebase_admin_ SDK. The channel will integrate with django-push-notifications_
    to streamline the process of dispatching notifications. The core edx-platform
    will handle authorization and manage Firebase credentials, ensuring secure and
    authenticated communication with the Firebase Cloud Messaging (FCM) service.
    Also, context collection for IOS devices using APNSConfig will be added to the channel
    for correct notification rendering.

To configure push notification from edx-platform side, the following settings should be updated:
  - `FIREBASE_CREDENTIALS_PATH` or `FIREBASE_CREDENTIALS` — add the Firebase credentials for the FCM service
     in the form of path to JSON file or as a Python dictionary directly in private settings;
  - `ACE_ENABLED_CHANNELS` — add the 'push_notification' channel to the list;
  - `ACE_ENABLED_POLICIES` — add policies for 'push_notification' to the list;
  - `PUSH_NOTIFICATIONS_SETTINGS` — settings for the django-push-notifications_ package;
  - `INSTALLED_APPS` - `push_notifications` app should be registered in the edx-platform `INSTALLED_APPS`.

To simplify configuration for Open edX operators, all new settings for mobile push notifications channel will be
initialized in plugin settings `openedx/core/djangoapps/ace_common/settings` in edx-platform.

To create a new push notification in edx-platform please follow the next steps:
  - Enable push notifications ACE channel and register a new FCM application by providing `FIREBASE_CREDENTIALS`.
  - Create a new message type class that extends existing `BaseMessageType` from
    `openedx.core.djangoapps.ace_common.message`, define the message type and its associated renderer.
    You can also use the existing classes like `EnrollEnrolled`, `AllowedEnroll`, and other,
    to send push notifications by extending the context with necessary attributes and creating
    a new template with notification text.
  - Create new `body.txt` and `subject.txt` templates to specify the push notification content,
    like it is done for email.
    Example path for the template is `lms/templates/instructor/edx_ace/enrollenrolled/push/body.txt`,
    and it's possible to override template with comprehensive theming.
  - Collect and provide the necessary context for the notification.
  - Call the `ace.send` method to send the push notification.

Consequences
------------

1. Adds a new push notification channel, enhancing the notification system's capabilities.
2. Allows real-time communication with users, improving engagement and user experience.
3. Seamless integration with existing edx-ace framework, maintaining consistency and reliability.
4. Utilizes django-push-notifications_ and firebase_admin_, leveraging robust
   and widely-used technologies for push notifications, easing implementation overall,
   and decreasing effort for maintanace of push notifications channel.
5. Increase of complexity in the Open edX notification system, requiring potential updates of related packages.
6. Dependency on Firebase Cloud Messaging (FCM) service, which introduces external service dependency risks
   for push notifications channel.


.. _django-push-notifications: https://github.com/jazzband/django-push-notifications/
.. _firebase_admin: https://github.com/firebase/firebase-admin-python/

