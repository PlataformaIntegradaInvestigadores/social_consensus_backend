# Merge pgvector ordering migration with jobs model migrations.

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("jobs", "0001_ensure_pgvector"),
        ("jobs", "0002_remove_status_field"),
    ]

    operations = []
