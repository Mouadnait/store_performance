# Generated by Django 5.0.7 on 2024-07-23 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0016_user_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='bio',
            field=models.CharField(blank=True, max_length=160, null=True),
        ),
    ]
