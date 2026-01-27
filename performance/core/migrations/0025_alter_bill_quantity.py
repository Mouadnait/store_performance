from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_billitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='quantity',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
