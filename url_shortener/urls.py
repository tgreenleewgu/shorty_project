from django.urls import path
from url_shortener import views

urlpatterns = [
    path('api/shorten/', views.ShortenURLView.as_view(), name='shorten_url'),
    path('s/<str:short_code>/', views.RedirectURLView.as_view(), name='redirect_url'),
    path('api/stats/<str:short_code>/', views.URLStatsView.as_view(), name='url_stats'),
    path('update-profile/', views.update_user_profile, name='update_profile'),
    path('api/analytics/', views.UserAnalyticsView.as_view(), name='user-analytics'),
    path('api/analytics/<str:short_code>/', views.DeleteURLView.as_view(), name='delete-url'),
    path("", views.home, name='home')
]