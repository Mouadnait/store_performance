# Generated by Django 5.0.7 on 2024-07-15 14:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_remove_billitem_bill_alter_billitem_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='billitem',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='billitem',
            name='description',
        ),
        migrations.RemoveField(
            model_name='billitem',
            name='price',
        ),
        migrations.CreateModel(
            name='BillDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('bill_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='details', to='core.billitem')),
            ],
        ),
    ]