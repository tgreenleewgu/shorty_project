from allauth.socialaccount.signals import social_account_added, social_account_updated
from django.dispatch import receiver
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from allauth.account.signals import user_logged_in

User = get_user_model()

@receiver(user_logged_in)
def handle_user_logged_in(sender, request, user=None, **kwargs):
    handle_social_login(sender, request, user=user, **kwargs)

@receiver(social_account_added)
@receiver(social_account_updated)
def handle_social_account_event(sender, request, sociallogin=None, **kwargs):
    handle_social_login(sender, request, user=sociallogin.user if sociallogin else None, sociallogin=sociallogin, **kwargs)

def handle_social_login(sender, request, user=None, sociallogin=None, **kwargs):
    print("[Signal Fired] user_logged_in or social_account_added/updated")

    try:
        if not sociallogin:
            sociallogin = kwargs.get("sociallogin")
        if not sociallogin:
            print("No sociallogin found in kwargs")
            return

        provider = sociallogin.account.provider
        data = sociallogin.account.extra_data

        print("Provider:", provider)
        print("Extra data:", data)

        if provider == "google":
            username = data.get("email", "google_user")
        elif provider == "github":
            username = data.get("login", "github_user")
        else:
            username = "unknown_user"

        request.session["username"] = username
        print(f"[Session Set] username = {username}")

    except Exception as e:
        print("Login session setup failed:", str(e))

