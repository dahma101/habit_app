"""Add partial unique index on lists.(user_id, title) for non-deleted rows."""

from django.db import migrations


class Migration(migrations.Migration):
    """Add PostgreSQL partial unique index on (user_id, title) WHERE deleted_at IS NULL."""

    dependencies = [
        ("lists", "0002_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE UNIQUE INDEX lists_user_title_unique_active
                ON lists (user_id, title)
                WHERE deleted_at IS NULL;
            """,
            reverse_sql="DROP INDEX IF EXISTS lists_user_title_unique_active;",
        ),
    ]
