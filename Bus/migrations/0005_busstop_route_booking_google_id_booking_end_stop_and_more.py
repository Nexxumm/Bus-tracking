# Generated by Django 5.1.5 on 2025-02-13 06:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bus', '0004_seatclass_booking_num_seats_alter_ticket_booking_otp_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusStop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=10, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('fare', models.PositiveIntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='booking',
            name='google_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='end_stop',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='end_booking', to='Bus.busstop'),
        ),
        migrations.AddField(
            model_name='booking',
            name='start_stop',
            field=models.ForeignKey(default=-1, on_delete=django.db.models.deletion.PROTECT, related_name='start_booking', to='Bus.busstop'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='RouteStop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField()),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Bus.route')),
                ('stop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Bus.busstop')),
            ],
            options={
                'ordering': ['order'],
                'unique_together': {('route', 'order'), ('route', 'stop')},
            },
        ),
        migrations.AddField(
            model_name='route',
            name='stops',
            field=models.ManyToManyField(through='Bus.RouteStop', to='Bus.busstop'),
        ),
    ]
