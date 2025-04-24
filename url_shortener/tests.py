from django.test import TestCase
from unittest.mock import patch
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import ErrorDetail
from django.http import Http404
from url_shortener.views import (
    RedirectURLView,
    DeleteURLView,
    UserAnalyticsView,
    ShortenURLView
)
from rest_framework import status


class URLShortenerTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @patch('url_shortener.views.get_urls_collection')
    def test_redirect_url_found(self, mock_get_urls_collection):
        mock_get_urls_collection.return_value.find_one.return_value = {
            '_id': 'mock_id',
            'original_url': 'https://example.com'
        }

        mock_get_urls_collection.return_value.update_one.return_value = None

        request = self.factory.get('/s/mock123')
        response = RedirectURLView.as_view()(request, short_code='mock123')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'https://example.com')

    @patch('url_shortener.views.get_urls_collection')
    def test_delete_url_success(self, mock_get_urls_collection):
        mock_result = type('MockResult', (), {'deleted_count': 1})()
        mock_get_urls_collection.return_value.delete_one.return_value = mock_result

        request = self.factory.delete('/api/delete/mock123')
        response = DeleteURLView.as_view()(request, short_code='mock123')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'URL deleted successfully')

    @patch('url_shortener.views.get_urls_collection')
    def test_delete_url_not_found(self, mock_get_urls_collection):
        mock_result = type('MockResult', (), {'deleted_count': 0})()
        mock_get_urls_collection.return_value.delete_one.return_value = mock_result

        request = self.factory.delete('/api/delete/fakecode')
        response = DeleteURLView.as_view()(request, short_code='fakecode')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'URL not found')

    @patch('url_shortener.views.get_urls_collection')
    def test_user_analytics_found(self, mock_get_urls_collection):
        mock_get_urls_collection.return_value.find.return_value = [
            {'original_url': 'https://test.com', 'short_code': 'abc123', 'clicks': 5}
        ]

        request = self.factory.get('/api/analytics?email=test@example.com')
        response = UserAnalyticsView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertEqual(response.data[0]['short_code'], 'abc123')

    @patch('url_shortener.views.get_urls_collection')
    def test_user_analytics_no_email(self, mock_get_urls_collection):
        request = self.factory.get('/api/analytics')
        response = UserAnalyticsView.as_view()(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Email parameter is required')
