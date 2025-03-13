from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .mongodb import get_urls_collection
from .utils import generate_short_code, generate_unique_id
from .serializers import URLShortenerSerializer

class ShortenURLView(APIView):
    """API view for shortening URLs"""
    
    def post(self, request, format=None):
        serializer = URLShortenerSerializer(data=request.data)
        if serializer.is_valid():
            original_url = serializer.validated_data['original_url']
            custom_code = serializer.validated_data.get('custom_code', '')
            
            urls_collection = get_urls_collection()
            
            # If custom code is provided, check if it's already in use
            if custom_code:
                existing_url = urls_collection.find_one({'short_code': custom_code})
                if existing_url:
                    return Response(
                        {'error': 'Custom code already in use'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                short_code = custom_code
            else:
                # Generate a unique random code
                while True:
                    short_code = generate_short_code()
                    existing_url = urls_collection.find_one({'short_code': short_code})
                    if not existing_url:
                        break
            
            # Create a new URL document
            url_document = {
                '_id': generate_unique_id(),
                'original_url': original_url,
                'short_code': short_code,
                'created_at': generate_unique_id().split('-')[0],  # Using timestamp part
                'clicks': 0
            }
            
            urls_collection.insert_one(url_document)
            
            # Construct the full shortened URL
            base_url = request.build_absolute_uri('/').rstrip('/')
            shortened_url = f"{base_url}/s/{short_code}"
            
            return Response({
                'original_url': original_url,
                'short_code': short_code,
                'shortened_url': shortened_url
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