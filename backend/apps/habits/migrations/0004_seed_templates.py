"""Data migration: seed ListTemplate and HabitTemplate records."""

import uuid

from django.db import migrations


LIST_TEMPLATES = [
    "Default",
    "Home",
    "Mental Clarity",
    "Health",
    "Self development",
]

HABIT_TEMPLATES = [
    ("Clean my room", "daily", "Home"),
    ("No Screens 30 minutes before bed", "daily", "Mental Clarity"),
    ("Workout", "daily", "Health"),
    ("Meal prepping", "twice_weekly", "Health"),
    ("Read a chapter from book", "twice_weekly", "Self development"),
]


def seed_templates(apps, schema_editor):  # type: ignore[no-untyped-def]
    """Insert template records that will be used for new user onboarding."""
    ListTemplate = apps.get_model("habits", "ListTemplate")
    HabitTemplate = apps.get_model("habits", "HabitTemplate")

    list_map = {}
    for title in LIST_TEMPLATES:
        lt = ListTemplate.objects.create(id=uuid.uuid4(), title=title)
        list_map[title] = lt

    for title, periodicity, list_title in HABIT_TEMPLATES:
        HabitTemplate.objects.create(
            id=uuid.uuid4(),
            title=title,
            periodicity=periodicity,
            list_template=list_map[list_title],
        )


def remove_templates(apps, schema_editor):  # type: ignore[no-untyped-def]
    """Reverse: delete all template records."""
    ListTemplate = apps.get_model("habits", "ListTemplate")
    ListTemplate.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("habits", "0003_initial"),
    ]

    operations = [
        migrations.RunPython(seed_templates, remove_templates),
    ]
