"""
Test cases for utils.braze
"""
from unittest.mock import patch

import pytest

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from edx_ace.utils.braze import get_braze_client

BRAZE_URL = "https://example.braze.com"
API_KEY = "test-api-key"
User = get_user_model()


@pytest.mark.django_db
class TestBrazeClient(TestCase):
    """ Test cases for utils.braze """

    @patch('edx_ace.utils.braze.BrazeClient')
    def test_disabled(self, mock_braze_client):
        """
        Test that the channel is settings aren't configured.
        """
        result = get_braze_client()
        self.assertEqual(result, None)
        mock_braze_client.assert_not_called()

    @override_settings(ACE_CHANNEL_BRAZE_API_KEY=API_KEY)
    @patch('edx_ace.utils.braze.BrazeClient')
    def test_braze_url_not_configured(self, mock_braze_client):
        """
        Test that the channel is settings aren't configured.
        """
        result = get_braze_client()
        self.assertEqual(result, None)
        mock_braze_client.assert_not_called()

    @override_settings(ACE_CHANNEL_BRAZE_REST_ENDPOINT=API_KEY)
    @patch('edx_ace.utils.braze.BrazeClient')
    def test_braze_api_key_not_configured(self, mock_braze_client):
        """
        Test that the channel is settings aren't configured.
        """
        result = get_braze_client()
        self.assertEqual(result, None)
        mock_braze_client.assert_not_called()

    @override_settings(ACE_CHANNEL_BRAZE_REST_ENDPOINT=API_KEY, ACE_CHANNEL_BRAZE_API_KEY=API_KEY)
    @patch('edx_ace.utils.braze.BrazeClient', return_value=True)
    def test_success(self, mock_braze_client):
        """
        Test that the channel is settings aren't configured.
        """
        result = get_braze_client()
        self.assertEqual(result, True)
        mock_braze_client.assert_called_once()
