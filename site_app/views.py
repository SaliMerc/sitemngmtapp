from datetime import datetime
import logging
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
# from .models import ....
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from site_app.models import DailyActivity, Issue, Image, Document, IssuePhoto, IssueDateReport, ActivityDateReport
from django.utils.timezone import now
from xhtml2pdf import pisa
from django.template.loader import get_template
# Create your views here.
logger = logging.getLogger(__name__)

def sign_up(request):
    error_message = None
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        # full_name= f"{first_name} {last_name}"
        email = request.POST.get("email")
        password = request.POST.get("password")
        conf_pass = request.POST.get("confirm_password")
        # error message displays
        if User.objects.filter(email=email).exists():
            error_message='A user with this email already exists'
            # messages.error(request, 'A user with this email already exists')
            return render(request, "login.html", {"error_message": error_message})
        if password != conf_pass:
            error_message='Passwords do not match'
            messages.error(request, 'Passwords do not match')
            return render(request, "signup.html",{"error_message": error_message})
        # print(username,password)
        myuser = User.objects.create_user(username=email, email=email, password=password, first_name=first_name, last_name=last_name)
        myuser.save()
        return redirect('login')
    return render(request, 'signup.html', {"error_message":error_message})
def log_in(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        myuser = authenticate( username=email, password=password)
        if myuser is not None:
            login(request, myuser)
            return redirect("dash")
        else:
            print("Invalid email or password")
            messages.error(request, "Invalid username or password")
            return redirect('login')
    return render(request, 'login.html')
def deleteData(request, id):
    actdel = DailyActivity.objects.get(id=id)
    issuedel= Issue.objects.get(id=id)
    actdel.delete()
    issuedel.delete()
    messages.success(request, 'Deleted successfully')
    return redirect("dash")
def dashpublic(request):
    return render(request, 'basepublic.html')
def index(request):
    return render(request, 'index.html')
@login_required
def dash(request):
    if request.user.is_authenticated:
        last_name=request.user.last_name
        print(f"Last Name: {last_name}")
        return render(request, 'dash.html', {'last_name':last_name})
    else:
        return redirect('login')
@login_required
def activitylog(request):
    if request.method == "POST":
        date=request.POST.get("date", now())
        site_open_time=request.POST.get("open-time", None)
        site_close_time=request.POST.get("close-time", None)
        work_completed=request.POST.get("work-completed")
        equipment_used=request.POST.get("equipment-used")
        materials_used=request.POST.get("material-used")
        site_type=request.POST.get("site-type")
        site_name=request.POST.get("site_name")
        images=request.FILES.getlist("images")
        documents=request.FILES.getlist("docs")
        user = request.user
        activity=DailyActivity(date=date, site_open_time=site_open_time, site_close_time=site_close_time, work_completed=work_completed, equipment_used=equipment_used, materials_used=materials_used,site_name=site_name,site_type=site_type,user=user)
        activity.save()
        for image in images:
            img = Image.objects.create(image=image, user=user)
            activity.progress_photos.add(img)

        for document in documents:
            doc = Document.objects.create(document=document, user=user)
            activity.relevant_documents.add(doc)
        activity.save()
        return redirect("activityview")
    existing_sites=DailyActivity.objects.values_list("site_name", flat=True).distinct().order_by("site_name")
    return render(request, 'activitylog.html', {"existing_sites":existing_sites})
@login_required
def activityview(request):
    activities=DailyActivity.objects.filter(user=request.user)
    return render(request, 'activityview.html',{'activities':activities})
@login_required
def activity_view(request,id):
    activities=DailyActivity.objects.filter(user=request.user,id=id)
    return render(request, 'activityview.html',{'activities':activities})
@login_required
def issuelog(request):
    if request.method == "POST":
        issue_date=request.POST.get("issue_date", now())
        issue_time=request.POST.get("issue_time", None)
        issue_description=request.POST.get("issue_description")
        images=request.FILES.getlist("images")
        resolution_steps=request.POST.get("resolution_steps")
        issue_status=request.POST.get("issue_status")
        site_type = request.POST.get("site-type")
        site_name = request.POST.get("site_name")
        user=request.user
        all_issues=Issue(issue_date=issue_date, issue_time=issue_time, issue_description=issue_description, resolution_steps=resolution_steps,issue_status=issue_status,site_name=site_name,site_type=site_type,user=user)
        all_issues.save()
        for image in images:
            img = IssuePhoto.objects.create(image=image, user=user)
            all_issues.issue_photos.add(img)
        all_issues.save()
        return redirect("issueview")
    existing_sites = Issue.objects.values_list("site_name", flat=True).distinct().order_by("site_name")
    return render(request, 'issuelog.html', {"existing_sites":existing_sites})
@login_required
def issueview(request,id):
    issues=Issue.objects.filter(user=request.user, id=id)
    return render(request, 'issueview.html', {'issues':issues})
@login_required
def issuelist(request):
    issues=Issue.objects.filter(user=request.user)
    return render(request, 'issueview.html', {'issues':issues})
# @login_required
# def activityupdate(request, id):
#     if request.method == "POST":
#         date = request.POST.get("date", now())
#         site_open_time = request.POST.get("open-time", None)
#         site_close_time = request.POST.get("close-time", None)
#         work_completed = request.POST.get("work-completed")
#         equipment_used = request.POST.get("equipment-used")
#         materials_used = request.POST.get("material-used")
#         site_type = request.POST.get("site-type")
#         site_name = request.POST.get("site_name")
#         images = request.FILES.getlist("images")
#         documents = request.FILES.getlist("docs")
#         user = request.user
#         activity=DailyActivity.objects.get(id=id, user=user)
#         activity.date = date
#         activity.site_open_time = site_open_time
#         activity.site_close_time = site_close_time
#         activity.work_completed = work_completed
#         activity.equipment_used = equipment_used
#         activity.materials_used = materials_used
#         activity.site_name = site_name
#         activity.site_type = site_type
#
#         for image in images:
#             img = Image.objects.create(image=image, user=user)
#             activity.progress_photos.add(img)
#
#         for document in documents:
#             doc = Document.objects.create(document=document, user=user)
#             activity.relevant_documents.add(doc)
#         activity.save()
#         return redirect("activityupdate")
#     activity = get_object_or_404(DailyActivity, id=id, user=request.user)
#     existing_sites = DailyActivity.objects.values_list("site_name", flat=True).distinct()
#     # d = DailyActivity.objects.get(id=id, user=request.user)
#     return render(request, 'activityupdate.html', {"existing_sites": existing_sites, "activity":activity})
# def issueupdate(request, id):
#     return render(request, 'issueupdate.html')
# @login_required
# def report_view(request):
#     dates = request.GET.getlist('dates')
#     activities = []
#     issues = []
#     if dates:
#         activities = DailyActivity.objects.filter(user=request.user, date__in=dates)
#         issues = Issue.objects.filter(user=request.user, issue_date__in=dates)
#     return render(request, 'reportform.html', {'activities': activities, 'issues': issues, 'dates': dates})

def report_view(request):
    issue_dates = Issue.objects.filter(user=request.user).values_list("issue_date", flat=True).distinct().order_by("issue_date")
    activity_dates=DailyActivity.objects.filter(user=request.user).values_list("date", flat=True).distinct().order_by("date")
    if request.method=="POST":
        issue_dates=request.POST.getlist("issue_dates")
        activity_dates=request.POST.getlist("activity_dates")
        for date_str in issue_dates:
            try:
                issue_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                IssueDateReport.objects.create(issue_date=issue_date, user=request.user)
            except ValueError:
                continue
        # for issue_date in issue_dates:
        #     IssueDateReport.objects.create(issue_dates=issue_date, user=request.user)
        for date_str in activity_dates:
            try:
                activity_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                ActivityDateReport.objects.create(activity_date=activity_date, user=request.user)
            except ValueError:
                continue
        # for activity_date in activity_dates:
        #     IssueDateReport.objects.create(activity_dates=activity_date, user=request.user)
        return redirect("dash")
    return render(request, 'reportform.html', {"issue_dates":issue_dates, "activity_dates":activity_dates})

