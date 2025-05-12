from django.urls import path
from url_shortener import views
from .views import EnsureCSRFCookieView

urlpatterns = [
    path('api/shorten/', views.ShortenURLView.as_view(), name='shorten_url'),
    path('s/<str:short_code>/', views.RedirectURLView.as_view(), name='redirect_url'),
    path('api/stats/<str:short_code>/', views.URLStatsView.as_view(), name='url_stats'),
    path('update-profile/', views.update_user_profile, name='update_profile'),
    path('api/analytics/', views.UserAnalyticsView.as_view(), name='user-analytics'),
    path('api/analytics/<str:short_code>/', views.DeleteURLView.as_view(), name='delete-url'),
    path("", views.home, name='home'),
    path("api/me/", views.user_info, name="get_current_user"),
    path("api/logout/", views.logout_view),
    path('api/csrf/', EnsureCSRFCookieView.as_view(), name='get_csrf_cookie'),
 


    
]
