from django.conf import settings


def user_settings(request):
    return {'user_default_avatar': "img/default_avatar.png", 'media_url': settings.MEDIA_URL}
