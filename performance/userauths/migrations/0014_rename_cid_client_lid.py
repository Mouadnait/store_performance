# Generated by Django 5.0.7 on 2024-07-17 09:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0013_remove_client_vid_client_cid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='client',
            old_name='cid',
            new_name='lid',
        ),
    ]