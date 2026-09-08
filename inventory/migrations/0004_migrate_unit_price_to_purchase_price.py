from django.db import migrations


def copy_unit_price_to_purchase_price(apps, schema_editor):
    Product = apps.get_model("inventory", "Product")

    for product in Product.objects.all():
        if product.purchase_price is None:
            product.purchase_price = product.unit_price
            product.save(update_fields=["purchase_price"])


def reverse_copy(apps, schema_editor):
    Product = apps.get_model("inventory", "Product")

    Product.objects.update(purchase_price=None)


class Migration(migrations.Migration):

    dependencies = [
        (
            "inventory",
            "0003_product_purchase_price_product_safety_stock_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(
            copy_unit_price_to_purchase_price,
            reverse_copy,
        ),
    ]