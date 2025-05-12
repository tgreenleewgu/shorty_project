# shortener/authentication.py
import jwt
import logging
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

logger = logging.getLogger(__name__)

class SupabaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        logger.debug("Starting authentication process")
        
        # Print ALL headers for debugging
        for key, value in request.META.items():
            if key.startswith('HTTP_'):
                logger.debug(f"Header {key}: {value}")
        
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        logger.debug(f"Authorization header: {auth_header}")
        
        if not auth_header or not auth_header.startswith('Bearer '):
            logger.debug("No Bearer token found in Authorization header")
            return None
        
        token = auth_header.split(' ')[1].strip()
        
        if not token:
            logger.debug("Empty token found")
            return None
            
        logger.debug(f"Token found: {token[:10]}...")
        
        try:
            # Verify JWT token
            payload = jwt.decode(
                token, 
                settings.SUPABASE_JWT_SECRET,
                algorithms=['HS256'],
                options={"verify_signature": True}
            )
            
            # Extract user info from the token
            user_id = payload.get('sub')
            email = payload.get('email')
            
            logger.debug(f"Token verified. User: {email}")
            
            # Create a simple user object
            user = type('SupabaseUser', (), {
                'id': user_id,
                'email': email,
                'is_authenticated': True
            })
            
            return (user, token)
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise AuthenticationFailed(f'Authentication error: {str(e)}')