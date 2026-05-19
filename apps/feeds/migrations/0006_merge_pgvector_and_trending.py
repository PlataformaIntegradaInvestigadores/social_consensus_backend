# Merge pgvector ordering migration with feed model migrations.

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("feeds", "0001_ensure_pgvector"),
        ("feeds", "0005_feedpost_trending_idx"),
    ]

    operations = []
