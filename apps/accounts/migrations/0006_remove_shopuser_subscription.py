# Generated by Django 5.1.7 on 2025-03-27 17:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_shopuser_subscription'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shopuser',
            name='subscription',
        ),
    ]
