# Generated by Django 5.0.2 on 2024-12-01 06:33

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.FileField(upload_to='sitefile')),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='siteprogress')),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DailyActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('site_open_time', models.TimeField(blank=True, null=True)),
                ('site_close_time', models.TimeField(blank=True, null=True)),
                ('work_completed', models.CharField(max_length=200)),
                ('equipment_used', models.CharField(max_length=200)),
                ('materials_used', models.CharField(max_length=200)),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('relevant_documents', models.ManyToManyField(blank=True, related_name='relevant_documents', to='site_app.document')),
                ('progress_photos', models.ManyToManyField(blank=True, related_name='progress_photos', to='site_app.image')),
            ],
        ),
        migrations.CreateModel(
            name='IssuePhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='siteissue')),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issue_date', models.DateField(default=django.utils.timezone.now)),
                ('issue_time', models.TimeField(blank=True, null=True)),
                ('issue_description', models.CharField(max_length=200)),
                ('resolution_steps', models.CharField(max_length=200)),
                ('issue_status', models.CharField(max_length=200)),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('issue_photos', models.ManyToManyField(blank=True, related_name='issue_photos', to='site_app.issuephoto')),
            ],
        ),
    ]