from django.shortcuts import render
from django.shortcuts import redirect
from django.http import Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from shorty_project.settings import LOGIN_REDIRECT_URL
from .mongodb import get_urls_collection
from .utils import generate_short_code, generate_unique_id
from .serializers import URLShortenerSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import jwt
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BaseAuthentication

from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialConnectView

class GitHubLogin(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    callback_url = LOGIN_REDIRECT_URL
    client_class = OAuth2Client

class GithubConnect(SocialConnectView):
    adapter_class = GitHubOAuth2Adapter
    callback_url = LOGIN_REDIRECT_URL
    client_class = OAuth2Client

from rest_framework.decorators import api_view, permission_classes
from .serializers import UserInfoSerializer
from rest_framework.permissions import IsAuthenticated

from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny



def get_current_user(request):
    username = request.session.get("username", "not-in-session")
    print("[/api/me/] Session username:", username)
    return JsonResponse({"username": username})


@method_decorator(ensure_csrf_cookie, name='dispatch')
class EnsureCSRFCookieView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"message": "CSRF cookie set"})



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_info(request):
    return Response({
        "username": request.user.username  
    })
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def logout_view(request):
    logout(request)
    return JsonResponse({"message": "Logged out"})
from django.http import HttpResponse
from django.utils.decorators import method_decorator


def home(request):
    print("logging home view", request.user.username)

    return HttpResponse("Hello, world. You're at the polls index.")

@csrf_exempt
def update_user_profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # username from the request
        user_id = request.user.id  # Assuming you have user authentication in place

        if not username:
            return JsonResponse({'error': 'username is required'}, status=400)

        # MongoDB query to find and update the user profile
        result = get_urls_collection().update_one(
            {'_id': user_id},  # Assuming user_id is stored in _id field
            {'$set': {'username': username}}  # Update username field
        )

        if result.matched_count == 0:
            return JsonResponse({'error': 'User not found'}, status=404)

        return JsonResponse({'message': 'User profile updated successfully!'})

    return JsonResponse({'error': 'Invalid request method!'}, status=400)

# Custom authentication class for Supabase
class SupabaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        try:
            # Verify JWT token using your Supabase JWT secret
            # You should store this in environment variables
            payload = jwt.decode(
                token, 
                'your-supabase-jwt-secret',  # Replace with your actual JWT secret
                algorithms=['HS256'],
                options={"verify_signature": True}
            )
            
            # Extract user info from the token
            user_id = payload.get('sub')
            username = payload.get('username')
            
            # Create a simple user object
            user = type('SupabaseUser', (), {
                'id': user_id,
                'username': username,
                'is_authenticated': True
            })
            
            return (user, token)
        except jwt.PyJWTError:
            return None

# Update your view to use the authentication
from rest_framework.permissions import AllowAny
# class ShortenURLView(APIView):
#     authentication_classes = [SupabaseAuthentication]
#     # permission_classes = [IsAuthenticated]
#     permission_classes = [AllowAny]
#     def post(self, request, format=None):
#         # Add username from authenticated user to the request data
#         data = request.data.copy()
        
#         # If the user is authenticated and has an username attribute
#         if hasattr(request.user, 'username') and request.user.username:
#             data['username'] = request.user.username
        
#         # Validate the data with the serializer
#         serializer = URLShortenerSerializer(data=data)
        
#         if serializer.is_valid():
#             original_url = serializer.validated_data['original_url']
#             custom_code = serializer.validated_data.get('custom_code', '')
#             username = serializer.validated_data['username']  # Now coming from the user
#             username = serializer.validated_data.get('username')

            
#             urls_collection = get_urls_collection()
            
#             if custom_code:
#                 existing_url = urls_collection.find_one({'short_code': custom_code})
#                 if existing_url:
#                     return Response({'error': 'Custom code already in use'}, status=status.HTTP_400_BAD_REQUEST)
#                 short_code = custom_code
#             else:
#                 while True:
#                     short_code = generate_short_code()
#                     existing_url = urls_collection.find_one({'short_code': short_code})
#                     if not existing_url:
#                         break
#             if hasattr(request.user, 'username') and request.user.username:
#                 data['username'] = request.user.username

#             url_document = {
#             '_id': generate_unique_id(),
#             'original_url': original_url,
#             'short_code': short_code,
#             'created_at': generate_unique_id().split('-')[0],
#             'clicks': 0,
#             'username': data['username'],
#         }


#             # url_document = {
#             #     '_id': generate_unique_id(),
#             #     'original_url': original_url,
#             #     'short_code': short_code,
#             #     'created_at': generate_unique_id().split('-')[0],
#             #     'clicks': 0,
#             #     'username': username,
                
#             # }
            
#             urls_collection.insert_one(url_document)
            
#             base_url = request.build_absolute_uri('/').rstrip('/')
#             shortened_url = f"{base_url}/s/{short_code}"
            
#             return Response({
#                 'original_url': original_url,
#                 'short_code': short_code,
#                 'shortened_url': shortened_url,
#                 'username': username
#             }, status=status.HTTP_201_CREATED)
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ShortenURLView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure user is authenticated via Django session

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
                'created_at': generate_unique_id().split('-')[0],
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


@method_decorator(ensure_csrf_cookie, name='dispatch')
class EnsureCSRFCookieView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({'message': 'CSRF cookie set'})


class RedirectURLView(APIView):
    """API view for redirecting shortened URLs"""
    
    def get(self, request, short_code, format=None):
        urls_collection = get_urls_collection()
        url_document = urls_collection.find_one({'short_code': short_code})
        
        if not url_document:
            raise Http404("Short URL not found")
        
        # Increment the click counter
        urls_collection.update_one(
            {'_id': url_document['_id']},
            {'$inc': {'clicks': 1}}
        )
        
        return redirect(url_document['original_url'])

class URLStatsView(APIView):
    """API view for getting URL statistics"""
    
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
    
# class UserAnalyticsView(APIView):
#     authentication_classes = [SupabaseAuthentication]
#     permission_classes = [AllowAny]  # or IsAuthenticated if you require authentication

#     def get(self, request):
#         # Ensure request.user exists and contains username
#         user = request.user
#         if not user or not getattr(user, 'username', None):
#             return Response({'error': 'User username not found or user is not authenticated.'}, status=status.HTTP_400_BAD_REQUEST)
        
#         username = user.username

#         # Debugging: log the username for verification
#         print(f"User username: {username}")

#         try:
#             urls_collection = get_urls_collection()
#             urls = list(urls_collection.find({'username': username}, {'_id': 0, 'original_url': 1, 'short_code': 1, 'clicks': 1}))

#             if not urls:
#                 return Response({'error': 'No URLs found for the user.'}, status=status.HTTP_404_NOT_FOUND)

#             return Response(urls, status=status.HTTP_200_OK)
        
#         except Exception as e:
#             # Log the error for debugging purposes
#             print(f"Error fetching user analytics: {e}")
#             return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class UserAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        username = request.user.username
        if not username:
            return Response({"error": "Username not found"}, status=400)

        urls_collection = get_urls_collection()
        urls = list(urls_collection.find(
            {'username': username},
            {'_id': 0, 'original_url': 1, 'short_code': 1, 'clicks': 1}
        ))

        return Response(urls, status=200)
    

######### validation for delete URL ###########
# class DeleteURLView(APIView):
#     authentication_classes = [SupabaseAuthentication]
#     permission_classes = [AllowAny]  # Swap to IsAuthenticated once auth is fully working

#     def delete(self, request, short_code):
#         user = request.user

#         # Basic validation
#         if not user or not getattr(user, 'username', None):
#             return Response({"error": "Unauthorized. username not found in token."}, status=status.HTTP_401_UNAUTHORIZED)

#         username = user.username
#         urls_collection = get_urls_collection()

#         # Try to delete only URLs that belong to the user
#         result = urls_collection.delete_one({
#             'short_code': short_code,
#             'username': username
#         })

#         if result.deleted_count == 0:
#             return Response({"error": "URL not found or you don't have permission to delete this."}, status=status.HTTP_404_NOT_FOUND)

#         return Response({"message": "URL deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


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
