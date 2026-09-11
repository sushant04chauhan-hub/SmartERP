from django.db import migrations


def migrate_pending_to_ordered(apps, schema_editor):
    PurchaseOrder = apps.get_model(
        "procurement",
        "PurchaseOrder",
    )

    PurchaseOrder.objects.filter(
        status="PENDING"
    ).update(
        status="ORDERED"
    )


def reverse_migration(apps, schema_editor):
    PurchaseOrder = apps.get_model(
        "procurement",
        "PurchaseOrder",
    )

    PurchaseOrder.objects.filter(
        status="ORDERED"
    ).update(
        status="PENDING"
    )


class Migration(migrations.Migration):

    dependencies = [
        (
            "procurement",
            "0006_supplier_is_active",
        ),
    ]

    operations = [
        migrations.RunPython(
            migrate_pending_to_ordered,
            reverse_migration,
        ),
    ]