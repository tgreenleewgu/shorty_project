from allauth.socialaccount.signals import social_account_added, social_account_updated
from django.dispatch import receiver
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(social_account_added)
@receiver(social_account_updated)
def populate_email_from_github(request, sociallogin, **kwargs):
    user = sociallogin.user
    if sociallogin.account.provider == 'github':
        # GitHub sometimes returns email in extra_data
        email = sociallogin.account.extra_data.get('email')
        
        # If not found, try GitHub's primary email API response
        if not email:
            emails = sociallogin.account.extra_data.get('emails', [])
            if isinstance(emails, list):
                primary = next((e for e in emails if e.get("primary")), None)
                if primary:
                    email = primary.get("email")
        
        # Save email to user model if it doesn't exist
        if email and not user.email:
            user.email = email
            user.save()
