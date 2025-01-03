# Generated by Django 5.0.2 on 2024-12-16 21:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site_app', '0009_alter_dailyactivity_equipment_used_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Transactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=16)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('mpesa_code', models.CharField(max_length=50, unique=True)),
                ('checkout_id', models.CharField(max_length=50, unique=True)),
                ('status', models.CharField(max_length=50)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
