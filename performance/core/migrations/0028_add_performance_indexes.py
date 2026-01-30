# Generated migration for adding database indexes

from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_alter_bill_date'),  # Updated to correct parent migration
    ]

    operations = [
        # Add indexes for frequently queried fields on Bill
        migrations.AddIndex(
            model_name='bill',
            index=models.Index(fields=['store_name', 'date'], name='bill_store_date_idx'),
        ),
        migrations.AddIndex(
            model_name='bill',
            index=models.Index(fields=['client', 'date'], name='bill_client_date_idx'),
        ),
        # Add indexes for Product
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['user', 'status'], name='product_user_status_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['featured', 'status'], name='product_featured_status_idx'),
        ),
        # Add index for Client
        migrations.AddIndex(
            model_name='client',
            index=models.Index(fields=['user', 'gpt5_enabled'], name='client_user_gpt5_idx'),
        ),
    ]
