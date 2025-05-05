from allauth.socialaccount.signals import social_account_added, social_account_updated
from django.dispatch import receiver
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model

from allauth.account.signals import user_logged_in
from django.dispatch import receiver

User = get_user_model()

@receiver(social_account_added)
@receiver(social_account_updated)
# def populate_email_from_github(request, sociallogin, **kwargs):
#     user = sociallogin.user
#     if sociallogin.account.provider == 'github':
#         # GitHub sometimes returns email in extra_data
#         email = sociallogin.account.extra_data.get('email')
        
#         # If not found, try GitHub's primary email API response
#         if not email:
#             emails = sociallogin.account.extra_data.get('emails', [])
#             if isinstance(emails, list):
#                 primary = next((e for e in emails if e.get("primary")), None)
#                 if primary:
#                     email = primary.get("email")
        
#         # Save email to user model if it doesn't exist
#         if email and not user.email:
#             user.email = email
#             user.save()


# from allauth.account.signals import user_logged_in
# from django.dispatch import receiver
# from allauth.socialaccount.models import SocialAccount

# @receiver(user_logged_in)
# def handle_google_login(sender, request, user, **kwargs):
#     try:
#         social_account = SocialAccount.objects.get(user=user, provider="google")
#         google_data = social_account.extra_data
#         google_username = google_data.get("name") or google_data.get("email") or "unknown"

#         request.session["username"] = google_username
#     except SocialAccount.DoesNotExist:
#         print("No Google social account found")

@receiver(user_logged_in)
def handle_any_login(sender, request, user=None, **kwargs):
    print("[Signal Fired] user_logged_in")

    try:
        sociallogin = kwargs.get("sociallogin")  # <-- this is where the actual login info is
        if not sociallogin:
            print("No sociallogin found in kwargs")
            return

        provider = sociallogin.account.provider
        data = sociallogin.account.extra_data

        print("Provider:", provider)
        print("Extra data:", data)

        if provider == "google":
            username = data.get("email", "google_user").split("@")[0]
        elif provider == "github":
            username = data.get("login", "github_user")
        else:
            username = "unknown_user"

        request.session["username"] = username
        print(f"[Session Set] username = {username}")

    except Exception as e:
        print("Login session setup failed:", str(e))
