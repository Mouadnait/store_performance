# Generated by Django 5.0.7 on 2024-07-18 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_remove_bill_bill_items_bill_amount_bill_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='stock',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=99999999999, null=True),
        ),
    ]
