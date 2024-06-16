# Generated by Django 5.0.1 on 2024-06-16 21:13

import apps.custom_auth.domain.entities.group
import apps.custom_auth.domain.entities.post
import apps.custom_auth.domain.entities.user
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('id', models.CharField(default=apps.custom_auth.domain.entities.user.generate_unique_id, editable=False, max_length=10, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('username', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=128)),
                ('scopus_id', models.CharField(blank=True, max_length=20, null=True)),
                ('investigation_camp', models.CharField(blank=True, max_length=100, null=True)),
                ('institution', models.CharField(blank=True, max_length=100, null=True)),
                ('email_institution', models.EmailField(blank=True, max_length=254, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('profile_picture', models.ImageField(blank=True, default='profile_pictures/default_profile_picture.png', null=True, upload_to=apps.custom_auth.domain.entities.user.get_profile_picture_filepath)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'USER',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.CharField(default=apps.custom_auth.domain.entities.group.generate_unique_id, editable=False, max_length=10, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='administered_groups', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'GROUP',
            },
        ),
        migrations.CreateModel(
            name='GroupUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='custom_auth.group')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'GROUP_USERS',
            },
        ),
        migrations.AddField(
            model_name='group',
            name='users',
            field=models.ManyToManyField(related_name='member_groups', through='custom_auth.GroupUser', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.CharField(default=apps.custom_auth.domain.entities.post.generate_unique_id, editable=False, max_length=10, primary_key=True, serialize=False)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'POST',
            },
        ),
        migrations.CreateModel(
            name='PostFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, null=True, upload_to=apps.custom_auth.domain.entities.post.get_post_file_filepath)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='custom_auth.post')),
            ],
            options={
                'db_table': 'POST_FILES',
            },
        ),
        migrations.CreateModel(
            name='ProfileInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('about_me', models.TextField(blank=True, null=True)),
                ('disciplines', models.JSONField(blank=True, default=list)),
                ('contact_info', models.JSONField(blank=True, default=dict)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile_information', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'INFORMATION',
            },
        ),
        migrations.AddConstraint(
            model_name='user',
            constraint=models.UniqueConstraint(condition=models.Q(('scopus_id__isnull', False)), fields=('scopus_id',), name='unique_scopus_id'),
        ),
    ]
