# Generated by Django 5.1.4 on 2025-01-03 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='bio',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='service_area',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
