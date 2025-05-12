# shorty_project URL Configuration

from django.contrib import admin
from django.urls import include, path
from url_shortener.views import GitHubLogin, GithubConnect,GoogleLogin, GoogleConnect
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from dj_rest_auth.registration.views import SocialConnectView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('url_shortener.urls')),
    path('accounts/', include('allauth.urls')),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/github/', GitHubLogin.as_view(), name='github_login'),
    path('dj-rest-auth/github/connect/', GithubConnect.as_view(), name='github_connect'),
    path('dj-rest-auth/google/', GoogleLogin.as_view(), name='google_login'),
    path('dj-rest-auth/google/connect/', GoogleConnect.as_view(), name='google_connect')
]
