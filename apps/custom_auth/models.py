from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
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


class ProfileInformation(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile_information')
    about_me = models.TextField(blank=True, null=True)
    disciplines = models.JSONField(default=list, blank=True)
    contact_info = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile Information"

    class Meta:
        db_table = 'INFORMATION'  # Especificar el nombre de la tabla


class Group(models.Model):
    id = models.CharField(max_length=10, primary_key=True,
                          default=generate_unique_id, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='administered_groups')
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='GroupUser', related_name='member_groups')

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'GROUP'


class GroupUser(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    class Meta:
        db_table = 'GROUP_USERS'


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(username)
        user = self.model(username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, password, **extra_fields)


def get_profile_picture_filepath(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('profile_pictures/', filename)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(max_length=10, primary_key=True,
                          default=generate_unique_id, editable=False)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    scopus_id = models.CharField(max_length=20, null=True, blank=True)
    investigation_camp = models.CharField(
        max_length=100, null=True, blank=True)
    institution = models.CharField(max_length=100, null=True, blank=True)
    email_institution = models.EmailField(null=True, blank=True)
    website = models.URLField(max_length=200, null=True, blank=True)
    profile_picture = models.ImageField(upload_to=get_profile_picture_filepath,
                                        default='profile_pictures/default_profile_picture.png', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if self.scopus_id == '':
            self.scopus_id = None
        try:
            this = User.objects.get(id=self.id)
            if this.profile_picture != self.profile_picture and this.profile_picture != 'apps/media/profile_pictures/default_profile_picture.png':
                this.profile_picture.delete(save=False)
        except:
            pass
        super(User, self).save(*args, **kwargs)

    class Meta:
        db_table = 'USER'
        constraints = [
            models.UniqueConstraint(
                fields=['scopus_id'],
                name='unique_scopus_id',
                condition=models.Q(scopus_id__isnull=False)
            )
        ]
