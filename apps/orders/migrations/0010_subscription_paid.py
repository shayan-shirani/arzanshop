# Generated by Django 5.1.7 on 2025-03-27 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_subscription_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='paid',
            field=models.BooleanField(default=False),
        ),
    ]
