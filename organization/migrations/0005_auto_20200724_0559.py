# Generated by Django 2.1.5 on 2020-07-24 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0004_auto_20200724_0526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='ticket',
            field=models.CharField(default='EPWRAGKWBW34OHSYFTOPBTPS16LM7129YNUOLFAFDL1NJL08TL', max_length=50),
        ),
    ]
