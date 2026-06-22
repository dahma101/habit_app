"""Data migration: create a test user (test@test.com / test) preloaded like a normal user.

Reproduces what UserService.register does for a real signup: default lists + habits from the
seeded templates, plus ~70 historical check-in logs spread over the last 90 days. Uses historical
models (apps.get_model) so it stays safe against future schema changes.
"""

import random
import uuid
from datetime import timedelta

from django.contrib.auth.hashers import make_password
from django.db import migrations
from django.utils import timezone

from apps.habits.analytics import calculate_due_window


TEST_USER_EMAIL = "test@test.com"


def create_test_user(apps, schema_editor):  # type: ignore[no-untyped-def]
    """Create the test user with preloaded lists, habits, and tracked logs (idempotent)."""
    User = apps.get_model("users", "User")
    if User.objects.filter(email=TEST_USER_EMAIL).exists():
        return

    HabitList = apps.get_model("lists", "HabitList")
    Habit = apps.get_model("habits", "Habit")
    HabitLog = apps.get_model("habits", "HabitLog")
    ListTemplate = apps.get_model("habits", "ListTemplate")
    HabitTemplate = apps.get_model("habits", "HabitTemplate")

    user = User.objects.create(
        id=uuid.uuid4(),
        email=TEST_USER_EMAIL,
        full_name="Test User",
        avatar="avatar1",
        password=make_password("test"),
        is_active=True,
        is_staff=False,
    )

    # --- Mirror UserService._preload_user_data: lists + habits from templates ---
    list_map: dict[str, object] = {}
    for template in ListTemplate.objects.all():
        is_default = template.title.lower() == "default"
        list_map[template.title] = HabitList.objects.create(
            id=uuid.uuid4(),
            title=template.title,
            user=user,
            is_default=is_default,
        )

    default_list = list_map.get("Default") or HabitList.objects.create(
        id=uuid.uuid4(),
        title="Default",
        user=user,
        is_default=True,
    )

    now = timezone.now()
    created_habits: list[object] = []
    for habit_template in HabitTemplate.objects.select_related("list_template").all():
        target_list = list_map.get(habit_template.list_template.title, default_list)
        due_from, due_to = calculate_due_window(habit_template.periodicity, now)
        habit = Habit.objects.create(
            id=uuid.uuid4(),
            title=habit_template.title,
            periodicity=habit_template.periodicity,
            list=target_list,
            user=user,
            due_from=due_from,
            due_to=due_to,
        )
        created_habits.append(habit)

    if not created_habits:
        return

    # --- Mirror UserService._seed_habit_logs: ~70 logs across the last 90 days ---
    target_count = 70
    window_days = 90
    daily_habits = [h for h in created_habits if h.periodicity == "daily"]
    monthly_habits = [h for h in created_habits if h.periodicity == "monthly"]

    # (habit, log_time) pairs to create.
    log_specs: list[tuple[object, object]] = []

    if daily_habits:
        log_specs.append((daily_habits[0], now - timedelta(days=random.randint(1, window_days - 1))))
    if monthly_habits:
        log_specs.append((monthly_habits[0], now - timedelta(days=random.randint(5, window_days - 1))))

    while len(log_specs) < target_count:
        habit = random.choice(created_habits)
        log_time = (now - timedelta(days=random.randint(1, window_days))).replace(
            hour=random.randint(6, 22), minute=random.randint(0, 59), second=0, microsecond=0
        )
        log_specs.append((habit, log_time))

    # created_at is auto_now_add, so bulk_create would stamp everything at "now". Insert first,
    # then backdate each row via .update() (which bypasses auto_now_add) for genuine history.
    for habit, log_time in log_specs:
        log = HabitLog.objects.create(id=uuid.uuid4(), habit=habit, user=user, list=habit.list)
        HabitLog.objects.filter(id=log.id).update(created_at=log_time, updated_at=log_time)


def remove_test_user(apps, schema_editor):  # type: ignore[no-untyped-def]
    """Reverse: delete the test user (cascades to their lists, habits, and logs)."""
    User = apps.get_model("users", "User")
    User.objects.filter(email=TEST_USER_EMAIL).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_partial_unique_email"),
        ("lists", "0003_partial_unique_title"),
        ("habits", "0006_add_as_many_as_possible"),
    ]

    operations = [
        migrations.RunPython(create_test_user, remove_test_user),
    ]
