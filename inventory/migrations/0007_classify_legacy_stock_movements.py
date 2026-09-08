from django.db import migrations


def classify_legacy_movements(apps, schema_editor):
    StockMovement = apps.get_model(
        "inventory",
        "StockMovement",
    )

    # Old stock-in records created by procurement
    # can be identified by their purchase-order note.
    for movement in StockMovement.objects.filter(
        movement_type="IN"
    ).iterator():

        note = (movement.note or "").strip()

        if note.lower().startswith("purchase order "):
            new_type = "PURCHASE"
        else:
            new_type = "ADJUSTMENT_IN"

        StockMovement.objects.filter(
            pk=movement.pk
        ).update(
            movement_type=new_type
        )

    # Sales did not exist yet, so old OUT records
    # are treated as manual stock adjustments.
    StockMovement.objects.filter(
        movement_type="OUT"
    ).update(
        movement_type="ADJUSTMENT_OUT"
    )


def reverse_classification(apps, schema_editor):
    StockMovement = apps.get_model(
        "inventory",
        "StockMovement",
    )

    StockMovement.objects.filter(
        movement_type="PURCHASE",
        note__istartswith="Purchase Order ",
    ).update(
        movement_type="IN"
    )

    StockMovement.objects.filter(
        movement_type="ADJUSTMENT_IN"
    ).update(
        movement_type="IN"
    )

    StockMovement.objects.filter(
        movement_type="ADJUSTMENT_OUT"
    ).update(
        movement_type="OUT"
    )


class Migration(migrations.Migration):

    dependencies = [
        (
            "inventory",
            "0006_alter_stockmovement_movement_type",
        ),
    ]

    operations = [
        migrations.RunPython(
            classify_legacy_movements,
            reverse_classification,
        ),
    ]