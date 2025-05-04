from django.apps import AppConfig


class UrlShortenerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'url_shortener'

    def ready(self):
        import url_shortener.signals