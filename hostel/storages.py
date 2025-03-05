from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

class StaticFileStorage(FileSystemStorage):
    def __init__(self, location=None, base_url=None):
        location = location or settings.STATIC_IMAGE_UPLOAD_PATH
        base_url = base_url or settings.STATIC_URL + 'clg_image/'
        super().__init__(location, base_url)
