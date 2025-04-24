from django.shortcuts import render
from django.shortcuts import redirect
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
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



@csrf_exempt
def update_user_profile(request):
    if request.method == 'POST':
        email = request.POST.get('email')  # Email from the request
        user_id = request.user.id  # Assuming you have user authentication in place

        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)

        # MongoDB query to find and update the user profile
        result = get_urls_collection().update_one(
            {'_id': user_id},  # Assuming user_id is stored in _id field
            {'$set': {'email': email}}  # Update email field
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
            email = payload.get('email')
            
            # Create a simple user object
            user = type('SupabaseUser', (), {
                'id': user_id,
                'email': email,
                'is_authenticated': True
            })
            
            return (user, token)
        except jwt.PyJWTError:
            return None

# Update your view to use the authentication
from rest_framework.permissions import AllowAny
class ShortenURLView(APIView):
    authentication_classes = [SupabaseAuthentication]
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    def post(self, request, format=None):
        # Add email from authenticated user to the request data
        data = request.data.copy()
        
        # If the user is authenticated and has an email attribute
        if hasattr(request.user, 'email') and request.user.email:
            data['email'] = request.user.email
        
        # Validate the data with the serializer
        serializer = URLShortenerSerializer(data=data)
        
        if serializer.is_valid():
            original_url = serializer.validated_data['original_url']
            custom_code = serializer.validated_data.get('custom_code', '')
            email = serializer.validated_data['email']  # Now coming from the user
            email = serializer.validated_data.get('email')

            
            urls_collection = get_urls_collection()
            
            if custom_code:
                existing_url = urls_collection.find_one({'short_code': custom_code})
                if existing_url:
                    return Response({'error': 'Custom code already in use'}, status=status.HTTP_400_BAD_REQUEST)
                short_code = custom_code
            else:
                while True:
                    short_code = generate_short_code()
                    existing_url = urls_collection.find_one({'short_code': short_code})
                    if not existing_url:
                        break
            
            url_document = {
                '_id': generate_unique_id(),
                'original_url': original_url,
                'short_code': short_code,
                'created_at': generate_unique_id().split('-')[0],
                'clicks': 0,
                'email': email,
                
            }
            
            urls_collection.insert_one(url_document)
            
            base_url = request.build_absolute_uri('/').rstrip('/')
            shortened_url = f"{base_url}/s/{short_code}"
            
            return Response({
                'original_url': original_url,
                'short_code': short_code,
                'shortened_url': shortened_url,
                'email': email
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
#         # Ensure request.user exists and contains email
#         user = request.user
#         if not user or not getattr(user, 'email', None):
#             return Response({'error': 'User email not found or user is not authenticated.'}, status=status.HTTP_400_BAD_REQUEST)
        
#         email = user.email

#         # Debugging: log the email for verification
#         print(f"User email: {email}")

#         try:
#             urls_collection = get_urls_collection()
#             urls = list(urls_collection.find({'email': email}, {'_id': 0, 'original_url': 1, 'short_code': 1, 'clicks': 1}))

#             if not urls:
#                 return Response({'error': 'No URLs found for the user.'}, status=status.HTTP_404_NOT_FOUND)

#             return Response(urls, status=status.HTTP_200_OK)
        
#         except Exception as e:
#             # Log the error for debugging purposes
#             print(f"Error fetching user analytics: {e}")
#             return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class UserAnalyticsView(APIView):
    authentication_classes = []  # Keep authentication disabled for now
    permission_classes = [AllowAny]  # Allow any user, no auth required

    def get(self, request):
        # Get the email from the request parameters
        email = request.query_params.get('email')
        
        if not email:
            return Response({"error": "Email parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Filter URLs by email
        urls_collection = get_urls_collection()
        urls = list(urls_collection.find(
            {'email': email},  # Filter by email
            {'_id': 0, 'original_url': 1, 'short_code': 1, 'clicks': 1}
        ))
        
        return Response(urls, status=status.HTTP_200_OK)
    

######### validation for delete URL ###########
# class DeleteURLView(APIView):
#     authentication_classes = [SupabaseAuthentication]
#     permission_classes = [AllowAny]  # Swap to IsAuthenticated once auth is fully working

#     def delete(self, request, short_code):
#         user = request.user

#         # Basic validation
#         if not user or not getattr(user, 'email', None):
#             return Response({"error": "Unauthorized. Email not found in token."}, status=status.HTTP_401_UNAUTHORIZED)

#         email = user.email
#         urls_collection = get_urls_collection()

#         # Try to delete only URLs that belong to the user
#         result = urls_collection.delete_one({
#             'short_code': short_code,
#             'email': email
#         })

#         if result.deleted_count == 0:
#             return Response({"error": "URL not found or you don't have permission to delete this."}, status=status.HTTP_404_NOT_FOUND)

#         return Response({"message": "URL deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class DeleteURLView(APIView):
    authentication_classes = []  # ✅ Disable auth for now
    permission_classes = [AllowAny]  # ✅ Allow all users

    def delete(self, request, short_code):
        urls_collection = get_urls_collection()

        result = urls_collection.delete_one({'short_code': short_code})

        if result.deleted_count == 0:
            return Response({'error': 'URL not found'}, status=404)

        return Response({'message': 'URL deleted successfully'}, status=200)