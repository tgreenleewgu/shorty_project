from django.test import TestCase, Client
from unittest.mock import patch
from bson import ObjectId
from datetime import datetime
from django.contrib.auth.models import User
from rest_framework.test import APIClient

class URLShortenerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # You must also set the session variable manually
        session = self.client.session
        session['username'] = self.user.username
        session.save()

    @patch('url_shortener.views.get_urls_collection')
    def test_delete_url_success(self, mock_collection):
        mock_result = type('MockResult', (), {'deleted_count': 1})()
        mock_collection.return_value.delete_one.return_value = mock_result

        response = self.client.delete('/api/analytics/test123/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'URL deleted successfully')

    @patch('url_shortener.views.get_urls_collection')
    def test_delete_url_not_found(self, mock_collection):
        mock_result = type('MockResult', (), {'deleted_count': 0})()
        mock_collection.return_value.delete_one.return_value = mock_result

        response = self.client.delete('/api/analytics/fakecode/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'URL not found or not owned by you')

    @patch('url_shortener.views.get_urls_collection')
    def test_user_analytics(self, mock_collection):
        mock_collection.return_value.find.return_value = [
            {
                'original_url': 'https://example.com',
                'short_code': 'abc123',
                'clicks': 5,
                'created_at': datetime.now()
            }
        ]

        response = self.client.get('/api/analytics/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertEqual(response.json()[0]['short_code'], 'abc123')

    @patch('url_shortener.views.get_urls_collection')
    def test_redirect_url_found(self, mock_collection):
        mock_collection.return_value.find_one.return_value = {
            '_id': ObjectId(),
            'original_url': 'https://redirect.com',
            'short_code': 'go123'
        }
        mock_collection.return_value.update_one.return_value = None

        response = self.client.get('/s/go123/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'https://redirect.com')

    @patch('url_shortener.views.get_urls_collection')
    def test_stats_view(self, mock_collection):
        mock_collection.return_value.find_one.return_value = {
            'original_url': 'https://example.com',
            'short_code': 'abc123',
            'created_at': datetime.now(),
            'clicks': 42
        }

        response = self.client.get('/api/stats/abc123/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['clicks'], 42)
