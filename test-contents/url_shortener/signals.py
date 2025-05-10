from allauth.socialaccount.signals import social_account_added, social_account_updated
from django.dispatch import receiver
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model

from allauth.account.signals import user_logged_in
from django.dispatch import receiver

User = get_user_model()

@receiver(social_account_added)
@receiver(social_account_updated)


@receiver(user_logged_in)
def handle_any_login(sender, request, user=None, **kwargs):
    print("[Signal Fired] user_logged_in")

    try:
        sociallogin = kwargs.get("sociallogin") 
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
