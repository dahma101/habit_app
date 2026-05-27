"""Add partial unique index on users.email for non-deleted rows."""

from django.db import migrations


class Migration(migrations.Migration):
    """Add PostgreSQL partial unique index on email WHERE deleted_at IS NULL."""

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE UNIQUE INDEX users_email_unique_active
                ON users (email)
                WHERE deleted_at IS NULL;
            """,
            reverse_sql="DROP INDEX IF EXISTS users_email_unique_active;",
        ),
    ]
