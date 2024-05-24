Implement Push Notification Channel
==================================================

Status
------

Proposed

Context
------

The goal of ACE framework is to provide extensible mechanism for extending delivery channels and policies.
However, as of May 2024, edx-ace supports various email delivery channels like django and Sailthru as well as third party API integration for Braze, but lacks support for direct mobile push notifications.
Adding push notifications delivery channel will enable real-time communication with users through their mobile devices, enhancing user engagement and ensuring timely delivery of important information.
Flexibility and seamless integration with the existing framework are priorities for this new notification channel.

Decision
------

Implement a new push notification system.
Data for push notifications must be formatted according to mobile push notification requirements.
It should be possible to add optional payloads for advanced functionality (e.g. data for notification actions).
Send formatted push notifications using the firebase_admin_ SDK.
Integration with django-push-notifications_ to simplify the process of sending notifications.
Use the existing `GCMDevice` model and `GCMDeviceViewSet` view from django-push-notifications_ to manage user device tokens.
Provide secure and authenticated communication with Firebase Cloud Messaging (FCM).

It should also be noted that django-push-notifications_ does not currently implement sending notifications to IOS devices using the FCM channel, although the FCM service itself supports it.
This means that support for IOS devices should be added on the edx-ace side.

This will involve:
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

To create a new push notification, on edx-platform side the following steps are required:
  - Create a new message type class that extends existing `BaseMessageType` from
    `openedx.core.djangoapps.ace_common.message`, defining the message type and its associated renderer.
    This will also allow you to use the existing classes like `EnrollEnrolled`, `AllowedEnroll`, etc.
    to send push notifications by simply extending the context where necessary and creating
    new templates with notification body.
  - Create new body.txt and subject.txt templates for the push notification content like how it is done for email.
    Example path: `lms/templates/instructor/edx_ace/enrollenrolled/push/body.txt`.
  - Collect the necessary context for the notifications.
  - Setup Firebase Cloud Messaging (FCM) credentials and configure the edx-platform
    to communicate with the FCM service.
  - Add `PushNotificationChannel` to the enabled channels in the setting.
  - Call the `ace.send` method to send the push notification.

Consequences
------

1. Adds a new push notification channel, enhancing the notification system's capabilities.
2. Allows real-time communication with users, improving engagement and user experience.
3. Seamless integration with existing edx-ace framework, maintaining consistency and reliability.
4. Utilizes django-push-notifications_ and firebase_admin_, leveraging robust and widely-used technologies for push notifications.
5. Additional complexity in the notification system, requiring maintenance and potential updates.
6. Dependency on Firebase Cloud Messaging (FCM) service, which might introduce external service dependency risks.


It was decided not to expand the codebase unnecessarily and not to independently implement
models and views for storing user device tokens, mechanisms for sending push notifications,
or mechanisms for deactivating inactive tokens, as all of this functionality is already
available in the django-push-notifications_ package. Therefore, it is better for edx-ace to
use the existing `GCMDevice` model, and on the edx-platform side, add the `GCMDeviceViewSet`
view to allow mobile devices to send their tokens.

.. _django-push-notifications: https://github.com/jazzband/django-push-notifications/
.. _firebase_admin: https://github.com/firebase/firebase-admin-python/
