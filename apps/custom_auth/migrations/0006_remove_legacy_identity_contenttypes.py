from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("custom_auth", "0005_drop_legacy_identity_models"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                IF to_regclass('public.auth_group_permissions') IS NOT NULL THEN
                    DELETE FROM auth_group_permissions
                    WHERE permission_id IN (
                        SELECT p.id
                        FROM auth_permission p
                        JOIN django_content_type ct ON ct.id = p.content_type_id
                        WHERE ct.app_label = 'custom_auth'
                          AND ct.model IN ('user', 'group', 'groupuser', 'profileinformation', 'magiclink')
                    );
                END IF;

                IF to_regclass('public.auth_user_user_permissions') IS NOT NULL THEN
                    DELETE FROM auth_user_user_permissions
                    WHERE permission_id IN (
                        SELECT p.id
                        FROM auth_permission p
                        JOIN django_content_type ct ON ct.id = p.content_type_id
                        WHERE ct.app_label = 'custom_auth'
                          AND ct.model IN ('user', 'group', 'groupuser', 'profileinformation', 'magiclink')
                    );
                END IF;

                DELETE FROM auth_permission
                WHERE content_type_id IN (
                    SELECT id
                    FROM django_content_type
                    WHERE app_label = 'custom_auth'
                      AND model IN ('user', 'group', 'groupuser', 'profileinformation', 'magiclink')
                );

                UPDATE django_admin_log
                SET content_type_id = NULL
                WHERE content_type_id IN (
                    SELECT id
                    FROM django_content_type
                    WHERE app_label = 'custom_auth'
                      AND model IN ('user', 'group', 'groupuser', 'profileinformation', 'magiclink')
                );

                DELETE FROM django_content_type
                WHERE app_label = 'custom_auth'
                  AND model IN ('user', 'group', 'groupuser', 'profileinformation', 'magiclink');
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
