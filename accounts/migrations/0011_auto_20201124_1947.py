# Generated by Django 3.1.1 on 2020-11-24 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_transaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkall',
            name='Is_winnerfound',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='checkall',
            name='Is_winnerset',
            field=models.BooleanField(default=False),
        ),
    ]
