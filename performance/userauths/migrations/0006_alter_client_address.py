# Generated by Django 5.0.7 on 2024-07-11 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0005_rename_client_client_full_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='address',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]