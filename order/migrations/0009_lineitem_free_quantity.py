# Generated by Django 4.2.4 on 2023-08-29 03:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0008_remove_shipment_date_shipped_shipment_failed_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lineitem',
            name='free_quantity',
            field=models.PositiveIntegerField(default=0),
        ),
    ]