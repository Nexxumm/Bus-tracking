# Generated by Django 5.1.5 on 2025-02-13 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bus', '0006_alter_booking_end_stop'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='email_otp',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.DeleteModel(
            name='OTP',
        ),
    ]
