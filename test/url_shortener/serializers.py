from rest_framework import serializers

class URLShortenerSerializer(serializers.Serializer):
    original_url = serializers.URLField(required=True)
    custom_code = serializers.CharField(required=False, allow_blank=True, max_length=20)
    username = serializers.CharField(required=True)

    def validate_original_url(self, value):
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("URL must start with http:// or https://")
        return value
    
    def validate_custom_code(self, value):
        from .utils import is_valid_custom_code
        if value and not is_valid_custom_code(value):
            raise serializers.ValidationError("Custom code must contain only alphanumeric characters")
        return value

class URLRedirectSerializer(serializers.Serializer):
    short_code = serializers.CharField(required=True)

class UserInfoSerializer(serializers.Serializer):
     username = serializers.CharField()