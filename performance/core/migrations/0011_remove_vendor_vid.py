# Generated by Django 5.0.7 on 2024-07-17 10:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_remove_billitem_quantity_remove_billitem_total_price_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vendor',
            name='vid',
        ),
    ]
