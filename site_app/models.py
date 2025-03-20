from datetime import timedelta, date

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class ItemManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(in_trash=False)

# class MyUser(AbstractBaseUser,PermissionsMixin):
#     first_name = models.CharField(max_length=30)
#     last_name = models.CharField(max_length=30)
#     username = models.CharField(max_length=30, unique=True, blank=True, null=True)
#     email = models.EmailField()
#     profile_picture = models.ImageField(upload_to='profile_pictures', blank=True, null=True)
#
#     USERNAME_FIELD = 'email'
#     def __str__(self):
#         return self.first_name


# Create your models here.
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


# mpesa verification
class Transactions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    phone_number=models.CharField(max_length=16)
    amount=models.DecimalField(decimal_places=2, max_digits=10)
    mpesa_code=models.CharField(max_length=50, unique=True)
    checkout_id=models.CharField(max_length=50, unique=True)
    status=models.CharField(max_length=50)
    timestamp=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.phone_number

class SubscriptionAmount(models.Model):
    monthly_subscription_amount = models.IntegerField(default=0)
    yearly_subscription_amount = models.IntegerField(default=0)

    def __int__(self):
        return self.monthly_subscription_amount

class Subscription(models.Model):
    SUBSCRIPTION_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    user=models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    subscription_type=models.CharField(max_length=200, null=True, blank=True, choices=SUBSCRIPTION_CHOICES, default='monthly')
    start_date=models.ForeignKey(Transactions, on_delete=models.CASCADE, null=True, blank=True)
    end_date=models.DateField()
    is_active=models.BooleanField(default=False)

    def calculate_end_date(self):
        if self.start_date:
            start_date = self.start_date.timestamp.date()
            if self.subscription_type == 'monthly':
                self.end_date = start_date + timedelta(days=30)
            elif self.subscription_type == 'yearly':
                self.end_date = start_date + timedelta(days=365)
        else:
            self.end_date = None

    def check_active_status(self):
        if self.end_date:
            self.is_active = date.today() <= self.end_date
        else:
            self.is_active = False

    def save(self, *args, **kwargs):
        self.calculate_end_date()
        self.check_active_status()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.first_name} - {self.subscription_type}"
