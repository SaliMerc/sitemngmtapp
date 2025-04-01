from datetime import datetime, timedelta, date

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

import pytz
import random
import string
import uuid

class ItemManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(in_trash=False)

# I can use this model to extend the django user model without redefining the whole user model architecture
# class MyUser(AbstractUser):
#     phone_number=PhoneNumberField(unique=True)
#     profile_picture = models.ImageField(upload_to='profile_pictures', blank=True, null=True)
#
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []
#     def __str__(self):
#         return self.first_name


# Create your models here.

# otp for email verification during signup
class OTP(models.Model):
    session_id = models.UUIDField(unique=True, primary_key=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_valid(self):
        # otp expires after 10 minutes
        now = datetime.now(pytz.utc)
        time_difference = now - self.created_at
        if time_difference.total_seconds() < 600:
            return True
        return False
    
    def generate_otp(self):
        self.code = ''.join(random.choices(string.digits, k=6))
        self.save()

class Image(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    image = models.ImageField(upload_to='siteprogress')
class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    document = models.FileField(upload_to='sitefile')
class DailyActivity(models.Model):
    STAGE_CHOICES = [
        ('project-planning', 'Project Planning Stage'),
        ('site-investigation', 'Site Preparation (Site Investigation, etc.)'),
        ('foundation-work', 'Foundation Work'),
        ('structural-work', 'Structural Work (RCs and Masonry Work)'),
        ('system-installation', 'System Installation (Electrical and Plumbing Works)'),
        ('finishing', 'Finishing (Plastering, Painting, Flooring, Fixtures)'),
        ('handover', 'Handover (To the Client)'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    date=models.DateField(default=now)
    site_open_time=models.TimeField(null=True, blank=True)
    site_close_time=models.TimeField(null=True, blank=True)
    site_type = models.CharField(max_length=100,null=True)
    site_name = models.CharField(max_length=100, null=True)
    work_completed=models.TextField()
    equipment_used=models.TextField()
    materials_used=models.TextField()
    construction_stage=models.CharField(max_length=100,null=True, blank=True, choices=STAGE_CHOICES, default='planning')
    progress_photos = models.ManyToManyField(Image, related_name='progress_photos', blank=True)
    relevant_documents = models.ManyToManyField(Document, related_name='relevant_documents', blank=True)
    in_trash = models.BooleanField(default=False)

    objects = ItemManager()
    all_objects = models.Manager()

    def delete(self, *args, **kwargs):
        self.in_trash = True
        self.save()

    def __str__(self):
        return self.work_completed

class IssuePhoto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    image = models.ImageField(upload_to='siteissue')

class Issue(models.Model):
    STATUS_CHOICES = [
        ('in-progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    site_type = models.CharField(max_length=100,null=True)
    site_name = models.CharField(max_length=100, null=True)
    issue_date=models.DateField(default=now)
    issue_time=models.TimeField(null=True, blank=True)
    issue_description=models.TextField()
    # the related name should be the same as that of the variable for it to work seamlessly
    issue_photos = models.ManyToManyField(IssuePhoto, related_name='issue_photos', blank=True)
    resolution_steps=models.TextField()
    issue_status=models.CharField(max_length=200, null=True, blank=True, choices=STATUS_CHOICES, default='in-progress')
    in_trash = models.BooleanField(default=False)

    objects = ItemManager()
    all_objects = models.Manager()

    def delete(self, *args, **kwargs):
        self.in_trash = True
        self.save()

    def __str__(self):
        return self.issue_description
class ActivityReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    site_name=models.CharField(max_length=100)
    def __str__(self):
        return self.site_name
class IssueReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    site_name=models.CharField(max_length=100)
    def __str__(self):
        return self.site_name


class SubscriptionAmount(models.Model):
    monthly_subscription_amount = models.IntegerField(default=0)
    yearly_subscription_amount = models.IntegerField(default=0)

    def __int__(self):
        return self.monthly_subscription_amount

# mpesa verification
class Transactions(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    SUBSCRIPTION_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    phone_number=models.CharField(max_length=16)
    amount=models.DecimalField(decimal_places=2, max_digits=10)
    mpesa_code=models.CharField(max_length=50, unique=True,null=True, blank=True)
    checkout_id=models.CharField(max_length=50, unique=True,null=True, blank=True)
    status = models.CharField(max_length=200, choices=STATUS_CHOICES,null=True, blank=True)
    subscription_type=models.CharField(max_length=200, null=True, blank=True, choices=SUBSCRIPTION_CHOICES, default='monthly')
    start_date=models.DateTimeField(null=True, blank=True)
    result_description=models.TextField(null=True, blank=True)

    def __str__(self):
        return self.status


