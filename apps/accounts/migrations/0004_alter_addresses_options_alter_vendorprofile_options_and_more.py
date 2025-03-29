# Generated by Django 5.1.7 on 2025-03-27 13:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_addresses_zip_code'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='addresses',
            options={'verbose_name': 'Address', 'verbose_name_plural': 'Addresses'},
        ),
        migrations.AlterModelOptions(
            name='vendorprofile',
            options={'verbose_name': 'Vendor Profile', 'verbose_name_plural': 'Vendor Profiles'},
        ),
        migrations.AlterUniqueTogether(
            name='addresses',
            unique_together={('user', 'is_default')},
        ),
    ]
