from django.db import models
from django.conf import settings
import os
import uuid
import string
import random


def get_post_file_filepath(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('post_files/', filename)


def generate_unique_id(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


class Post(models.Model):
    id = models.CharField(max_length=10, primary_key=True,
                          default=generate_unique_id, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='posts')
    description = models.TextField()
    created_at = models.DateTimeField(
        null=True, blank=True)  # Allow null and blank

    class Meta:
        db_table = 'POST'


class PostFile(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(
        upload_to=get_post_file_filepath, blank=True, null=True)

    class Meta:
        db_table = 'POST_FILES'
