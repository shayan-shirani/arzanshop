# Generated by Django 5.1.7 on 2025-03-27 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0012_alter_subscription_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
