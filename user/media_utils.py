import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage


def get_image_path(instance, filename):
    return os.path.join('profile_images', "{}".format(instance.id), filename)


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name
