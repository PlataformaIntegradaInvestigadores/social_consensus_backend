from django.contrib import admin
from apps.concensus.domain.entities.group import Group
from apps.concensus.domain.entities.topic import Topic

# Register your models here.

admin.site.register(Group)
admin.site.register(Topic)