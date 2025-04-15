"""
Helper Methods related to braze client
"""

try:
    from braze.client import BrazeClient
except ImportError:
    BrazeClient = None
from django.conf import settings


def get_braze_client():
    """ Returns a Braze client. """
    if not BrazeClient:
        return None

    braze_api_key = getattr(settings, 'EDX_BRAZE_API_KEY', None)
    braze_api_url = getattr(settings, 'EDX_BRAZE_API_SERVER', None)

    if not braze_api_key or not braze_api_url:
        return None

    return BrazeClient(
        api_key=braze_api_key,
        api_url=braze_api_url,
        app_id='',
    )
