# Generated by Django 4.2.4 on 2023-08-23 14:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_shipment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='return_of_order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='order.order'),
        ),
    ]
