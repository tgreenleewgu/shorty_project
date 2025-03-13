from django.urls import path
from .views import ShortenURLView, RedirectURLView, URLStatsView

urlpatterns = [
    path('api/shorten/', ShortenURLView.as_view(), name='shorten_url'),
    path('s/<str:short_code>/', RedirectURLView.as_view(), name='redirect_url'),
    path('api/stats/<str:short_code>/', URLStatsView.as_view(), name='url_stats'),
]

