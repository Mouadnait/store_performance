# Generated by Django 5.0.7 on 2024-07-12 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_category_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='old_price',
            field=models.DecimalField(decimal_places=2, default=1.0, max_digits=99999999999),
        ),
    ]
