# Generated by Django 5.1.4 on 2025-01-03 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_alter_service_options_remove_service_average_rating_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='status',
            field=models.CharField(choices=[('available', 'Available'), ('unavailable', 'Unavailable'), ('inactive', 'Inactive')], default='available', max_length=20),
        ),
        migrations.AlterField(
            model_name='service',
            name='location',
            field=models.CharField(max_length=200),
        ),
    ]