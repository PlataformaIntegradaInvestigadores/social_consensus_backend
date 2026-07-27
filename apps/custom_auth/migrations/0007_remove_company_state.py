from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("jobs", "0006_move_company_to_jobs"),
        ("custom_auth", "0006_remove_legacy_identity_contenttypes"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(
                    name="Company",
                ),
            ],
        ),
    ]
