from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


# Create your models here.
class Image(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    image = models.ImageField(upload_to='siteprogress')
class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    document = models.FileField(upload_to='sitefile')
class DailyActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    date=models.DateField(default=now)
    site_open_time=models.TimeField(null=True, blank=True)
    site_close_time=models.TimeField(null=True, blank=True)
    site_type = models.CharField(max_length=100,null=True)
    site_name = models.CharField(max_length=100, null=True)
    work_completed=models.TextField()
    equipment_used=models.TextField()
    materials_used=models.TextField()
    progress_photos = models.ManyToManyField(Image, related_name='progress_photos', blank=True)
    relevant_documents = models.ManyToManyField(Document, related_name='relevant_documents', blank=True)

    def __str__(self):
        return self.work_completed
# class Activity(models.Model):
#     all_activity=models.ForeignKey(DailyActivity, on_delete=models.CASCADE)
#     def __str__(self):
#         return self.all_activity
class IssuePhoto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    image = models.ImageField(upload_to='siteissue')

class Issue(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    site_type = models.CharField(max_length=100,null=True)
    site_name = models.CharField(max_length=100, null=True)
    issue_date=models.DateField(default=now)
    issue_time=models.TimeField(null=True, blank=True)
    issue_description=models.TextField()
    # the related name should be the same as that of the variable for it to work seamlessly
    issue_photos = models.ManyToManyField(IssuePhoto, related_name='issue_photos', blank=True)
    resolution_steps=models.TextField()
    issue_status=models.CharField(max_length=200)
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