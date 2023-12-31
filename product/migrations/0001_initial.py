# Generated by Django 4.2.2 on 2023-07-27 03:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("image", models.CharField(max_length=255)),
                ("name", models.CharField(max_length=100)),
                ("brand", models.CharField(max_length=50)),
                ("weight", models.DecimalField(decimal_places=2, max_digits=5)),
                ("color", models.CharField(max_length=20)),
                ("manufacturer", models.CharField(max_length=50)),
                ("origin", models.CharField(max_length=50)),
                ("description", models.TextField()),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                "db_table": "product",
            },
        ),
        migrations.CreateModel(
            name="Stock",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("province", models.CharField(max_length=50)),
                ("district", models.CharField(max_length=50)),
                ("ward", models.CharField(max_length=50)),
                ("address_line", models.CharField(max_length=200)),
            ],
            options={
                "db_table": "stock",
            },
        ),
        migrations.CreateModel(
            name="StockProduct",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.IntegerField()),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stock_products",
                        to="product.product",
                    ),
                ),
                (
                    "stock",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stock_products",
                        to="product.stock",
                    ),
                ),
            ],
            options={
                "db_table": "product_stock",
            },
        ),
    ]
