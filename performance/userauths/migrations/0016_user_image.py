# Generated by Django 5.0.7 on 2024-07-23 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0015_delete_client'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='image',
            field=models.ImageField(default='user.jpg', upload_to='user'),
        ),
    ]
