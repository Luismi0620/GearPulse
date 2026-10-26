from django.db import migrations

PLANS = [
    {"name": "monthly", "price": "9.99", "duration_days": 30},
    {"name": "quarterly", "price": "24.99", "duration_days": 90},
    {"name": "yearly", "price": "89.99", "duration_days": 365},
]


def seed_plans(apps, schema_editor):
    PlanModel = apps.get_model("subscriptions", "PlanModel")
    for plan in PLANS:
        PlanModel.objects.update_or_create(name=plan["name"], defaults=plan)


def remove_plans(apps, schema_editor):
    PlanModel = apps.get_model("subscriptions", "PlanModel")
    PlanModel.objects.filter(name__in=[p["name"] for p in PLANS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("subscriptions", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_plans, remove_plans),
    ]
