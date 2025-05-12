from .mongodb import get_urls_collection
from .serializers import URLShortenerSerializer, UserInfoSerializer
from .utils import generate_short_code, generate_unique_id

from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView, SocialConnectView

from datetime import datetime, timezone

from django.contrib.auth import logout
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from shorty_project.settings import LOGIN_REDIRECT_URL
from django.conf import settings



class GitHubLogin(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    callback_url = LOGIN_REDIRECT_URL
    client_class = OAuth2Client


class GithubConnect(SocialConnectView):
    adapter_class = GitHubOAuth2Adapter
    callback_url = LOGIN_REDIRECT_URL
    client_class = OAuth2Client


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.LOGIN_REDIRECT_URL
    client_class = OAuth2Client

class GoogleConnect(SocialConnectView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.LOGIN_REDIRECT_URL
    client_class = OAuth2Client

def get_current_user(request):
    username = request.session.get("username", "not-in-session")
    return JsonResponse({"username": username})


@method_decorator(ensure_csrf_cookie, name='dispatch')
class EnsureCSRFCookieView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"message": "CSRF cookie set"})


@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'message': 'CSRF cookie set'})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_info(request):
    return Response({
        "username": request.user.username
    })


@csrf_exempt
def logout_view(request):
    logout(request)
    return JsonResponse({"message": "Logged out"})


def home(request):
    print("logging home view", request.user.username)
    return HttpResponse("Hello, world. You're at the polls index.")


@csrf_exempt
def update_user_profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        user_id = request.user.id

        if not username:
            return JsonResponse({'error': 'username is required'}, status=400)

        result = get_urls_collection().update_one(
            {'_id': user_id},
            {'$set': {'username': username}}
        )

        if result.matched_count == 0:
            return JsonResponse({'error': 'User not found'}, status=404)

        return JsonResponse({'message': 'User profile updated successfully!'})

    return JsonResponse({'error': 'Invalid request method!'}, status=400)


class ShortenURLView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        data = request.data.copy()
        if hasattr(request.user, 'username') and request.user.username:
            data['username'] = request.user.username
        else:
            return Response({'error': 'Username not found in request'}, status=status.HTTP_403_FORBIDDEN)

        serializer = URLShortenerSerializer(data=data)
        if serializer.is_valid():
            original_url = serializer.validated_data['original_url']
            custom_code = serializer.validated_data.get('custom_code', '')
            username = serializer.validated_data['username']

            urls_collection = get_urls_collection()

            if custom_code:
                existing_url = urls_collection.find_one({'short_code': custom_code})
                if existing_url:
                    return Response({'error': 'Custom code already in use'}, status=status.HTTP_400_BAD_REQUEST)
                short_code = custom_code
            else:
                while True:
                    short_code = generate_short_code()
                    if not urls_collection.find_one({'short_code': short_code}):
                        break

            url_document = {
                '_id': generate_unique_id(),
                'original_url': original_url,
                'short_code': short_code,
                'created_at': datetime.now(timezone.utc),
                'clicks': 0,
                'username': username,
            }

            urls_collection.insert_one(url_document)

            base_url = request.build_absolute_uri('/').rstrip('/')
            shortened_url = f"{base_url}/s/{short_code}"

            return Response({
                'original_url': original_url,
                'short_code': short_code,
                'shortened_url': shortened_url,
                'username': username
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RedirectURLView(APIView):
    def get(self, request, short_code, format=None):
        urls_collection = get_urls_collection()
        url_document = urls_collection.find_one({'short_code': short_code})

        if not url_document:
            raise Http404("Short URL not found")

        urls_collection.update_one(
            {'_id': url_document['_id']},
            {'$inc': {'clicks': 1}}
        )

        return redirect(url_document['original_url'])


class URLStatsView(APIView):
    def get(self, request, short_code, format=None):
        urls_collection = get_urls_collection()
        url_document = urls_collection.find_one({'short_code': short_code})

        if not url_document:
            raise Http404("Short URL not found")

        return Response({
            'original_url': url_document['original_url'],
            'short_code': url_document['short_code'],
            'created_at': url_document['created_at'],
            'clicks': url_document['clicks']
        })


class UserAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        username = request.user.username
        if not username:
            return Response({"error": "Username not found"}, status=400)

        urls_collection = get_urls_collection()
        urls = list(urls_collection.find(
            {'username': username},
            {'_id': 0, 'original_url': 1, 'short_code': 1, 'clicks': 1, 'created_at': 1}
        ))

        for url in urls:
            raw_created = url.get('created_at')
            try:
                if isinstance(raw_created, datetime):
                    parsed = raw_created
                else:
                    parsed = datetime.fromisoformat(str(raw_created))
                url['created_at'] = parsed.isoformat()
            except Exception:
                url['created_at'] = None

        return Response(urls, status=200)


class DeleteURLView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, short_code):
        username = request.user.username
        if not username:
            return Response({"error": "Unauthorized"}, status=401)

        urls_collection = get_urls_collection()
        result = urls_collection.delete_one({
            'short_code': short_code,
            'username': username
        })

        if result.deleted_count == 0:
            return Response({'error': 'URL not found or not owned by you'}, status=404)

        return Response({'message': 'URL deleted successfully'}, status=200)
