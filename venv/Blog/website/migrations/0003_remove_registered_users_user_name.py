# Generated by Django 5.0.4 on 2024-05-19 15:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_remove_custom_users_user_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registered_users',
            name='user_name',
        ),
    ]
