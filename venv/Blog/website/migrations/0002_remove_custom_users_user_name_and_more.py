# Generated by Django 5.0.4 on 2024-05-19 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='custom_users',
            name='user_name',
        ),
        migrations.AddField(
            model_name='registered_users',
            name='user_name',
            field=models.CharField(default=True, max_length=100, unique=True),
            preserve_default=False,
        ),
    ]
