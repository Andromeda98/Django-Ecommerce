# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_alter_product_description'),
        ('payment', '0005_order_date_shipped'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Product',
            new_name='Book',
        ),
    ]
