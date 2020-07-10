# Generated by Django 2.1.5 on 2020-07-24 06:44

from django.db import migrations, models
import organization.models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0005_auto_20200724_0559'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='ticket',
            field=models.CharField(default=organization.models.Service.generate_ticket, max_length=50),
        ),
    ]
