# Generated by Django 5.0.7 on 2024-07-15 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_remove_billitem_amount_remove_billitem_description_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='billitem',
            name='quantity',
        ),
        migrations.RemoveField(
            model_name='billitem',
            name='total_price',
        ),
        migrations.AddField(
            model_name='billdetail',
            name='quantity',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='billdetail',
            name='total_price',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
            preserve_default=False,
        ),
    ]