from datetime import datetime
from django.contrib.sites import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
# from .models import ....
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import pytz

from SiteLogger import settings
from site_app.models import DailyActivity, Issue, Image, Document, IssuePhoto, ActivityReport, IssueReport, Transactions
from django.utils.timezone import now
from datetime import date
from django.template.loader import get_template
from requests.auth import HTTPBasicAuth
import json
from . credentials import MpesaAccessToken, LipanaMpesaPassword,MpesaC2bCredential
import requests
# for emails
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.conf import settings


def sign_up(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        conf_pass = request.POST.get("confirm_password")
        if User.objects.filter(email=email).exists():
            messages.error(request, 'A user with this email already exists')
            return render(request, "login.html")
        if password != conf_pass:
            messages.error(request, 'Passwords do not match')
            return render(request, "signup.html")
        # print(username,password)
        myuser = User.objects.create_user(username=email, email=email, password=password, first_name=first_name, last_name=last_name)
        myuser.save()
        return redirect('login')
    return render(request, 'signup.html')
def log_in(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        myuser = authenticate( username=email, password=password)
        if myuser is not None:
            login(request, myuser)
            return redirect("dash")
        else:
            # print("Invalid email or password")
            messages.error(request, "Invalid username or password")
            return redirect('login')
    return render(request, 'login.html')

# reset password starts here

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            token = token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = request.build_absolute_uri(reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token}))
            message = render_to_string('password_reset_email.html', {'reset_link': reset_link})
            send_mail(
                'Password Reset Request',
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False, )
            messages.success(request, 'A password reset link has been sent to your email.')
        else:
            messages.error(request, 'Email address not found.')
        return redirect('forgot_password')
    return render(request, 'forgot_password.html')

# confirm password reset
def password_reset_confirm(request, uidb64, token):
    if request.method == "POST":
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        if token_generator.check_token(user, token):
            password = request.POST.get("password")
            conf_pass = request.POST.get("confirm_password")
            if password == conf_pass:
                user.set_password(password)
                user.save()
                messages.success(request, 'Your password has been reset successfully.')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match.')
    return render(request, 'password_reset_confirm.html')


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
def basedash(request):
    if request.user.is_authenticated:
        last_name = request.user.last_name
    return render(request, 'basedash.html', {'last_name': last_name})
@login_required
def dash(request):
    if request.user.is_authenticated:
        last_name=request.user.last_name
        issues = Issue.objects.filter(user=request.user)
        activities = DailyActivity.objects.filter(user=request.user)
        print(f"Last Name: {last_name}")
        return render(request, 'dash.html', {'last_name':last_name, "issues":issues, "activities":activities})
    else:
        return redirect('login')
@login_required
def activitylog(request):
    if request.user.is_authenticated:
        last_name = request.user.last_name
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
    # existing_sites=DailyActivity.objects.values_list("site_name", flat=True).distinct().order_by("site_name")
    existing_sites = DailyActivity.objects.filter(user=request.user).values_list("site_name", flat=True).distinct().order_by("site_name")
    return render(request, 'activitylog.html', {"existing_sites":existing_sites, "last_name":last_name})
@login_required
def activityview(request):
    if request.user.is_authenticated:
        last_name = request.user.last_name
    activities=DailyActivity.objects.filter(user=request.user)
    return render(request, 'activityview.html',{'activities':activities, "last_name":last_name})
@login_required
def activity_view(request,id):
    if request.user.is_authenticated:
        last_name = request.user.last_name
    activities=DailyActivity.objects.filter(user=request.user,id=id)
    return render(request, 'activityview.html',{'activities':activities, "last_name":last_name})
@login_required
def issuelog(request):
    if request.user.is_authenticated:
        last_name = request.user.last_name
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
    # existing_sites = Issue.objects.values_list("site_name", flat=True).distinct().order_by("site_name")
    existing_sites = Issue.objects.filter(user=request.user).values_list("site_name",flat=True).distinct().order_by("site_name")
    return render(request, 'issuelog.html', {"existing_sites":existing_sites, "last_name":last_name})
@login_required
def issue_view(request):
    if request.user.is_authenticated:
        last_name = request.user.last_name
    issues=Issue.objects.filter(user=request.user)
    return render(request, 'issueview.html', {'issues':issues, "last_name":last_name})
@login_required
def issueview(request,id):
    if request.user.is_authenticated:
        last_name = request.user.last_name
    issues=Issue.objects.filter(user=request.user, id=id)
    return render(request, 'issueview.html', {'issues':issues, "last_name":last_name})
@login_required
def issuelist(request):
    if request.user.is_authenticated:
        last_name = request.user.last_name
    issues=Issue.objects.filter(user=request.user)
    return render(request, 'issueview.html', {'issues':issues, "last_name":last_name})
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
@login_required
def activity_report(request):
    if request.user.is_authenticated:
        last_name = request.user.last_name
    if request.method=="POST":
        site_name2=request.POST.get("site_activity_name")
        user = request.user
        query=ActivityReport(site_name=site_name2,user=user)
        query.save()
        return redirect("activityreportdisplay", id=query.id)
    site_names = DailyActivity.objects.filter(user=request.user).values_list("site_name",flat=True).distinct().order_by("site_name")
    return render(request, 'activityreport.html', {'site_names':site_names, "last_name":last_name})
@login_required
def activity_report_display(request, id):
    if request.user.is_authenticated:
        last_name = request.user.last_name
    user = request.user
    nairobi_tz = pytz.timezone('Africa/Nairobi')
    current_time = timezone.localtime(timezone.now(), nairobi_tz)
    from_report=ActivityReport.objects.get(id=id)
    site_name = from_report.site_name
    activities = DailyActivity.objects.filter(user=user, site_name=site_name).order_by("date")
    return render(request, 'activity_report_display.html',{"activities":activities, "user": user, "site_name":site_name, "last_name":last_name,"current_time":current_time})
@login_required
def issue_report(request):
    if request.user.is_authenticated:
        last_name = request.user.last_name
    if request.method=="POST":
        site_name1=request.POST.get("site_issue_name")
        user = request.user
        query=IssueReport(site_name=site_name1,user=user)
        query.save()
        return redirect("issuereportdisplay", id=query.id)
    site_names = Issue.objects.filter(user=request.user).values_list("site_name",flat=True).distinct().order_by("site_name")
    return render(request, 'issue_report.html', {'site_names': site_names, "last_name":last_name})
@login_required
def issue_display(request,id):
    if request.user.is_authenticated:
        last_name = request.user.last_name
    user=request.user
    site_in_report=IssueReport.objects.get(id=id)
    site_name=site_in_report.site_name
    issue_new=Issue.objects.filter(user=user, site_name=site_name).order_by("issue_date")
    return render(request, 'issue_report_display.html', {"user":user, "site_name":site_name, "issue_new":issue_new, "last_name":last_name})

# api integration starts here
@login_required
def token(request):
    consumer_key = MpesaC2bCredential.consumer_key
    consumer_secret = MpesaC2bCredential.consumer_secret
    api_URL = MpesaC2bCredential.api_URL

    r = requests.get(api_URL, auth=HTTPBasicAuth(
        consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token["access_token"]

    return render(request, 'token.html', {"token":validated_mpesa_access_token})

@login_required
def pay(request):
    if request.method == "POST":
        phone = request.POST['phone']
        amount = request.POST['amount']
        access_token = MpesaAccessToken.validated_mpesa_access_token
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer %s" % access_token}
        request_data = {
            "BusinessShortCode": LipanaMpesaPassword.Business_short_code,
            "Password": LipanaMpesaPassword.decode_password,
            "Timestamp": LipanaMpesaPassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": LipanaMpesaPassword.Business_short_code,
            "PhoneNumber": phone,
            # this should be a public url maybe from the hosted site or ngrok etc
            "CallBackURL":MpesaC2bCredential.callback_url,
            "AccountReference": "Mercy Saline",
            "TransactionDesc": "Site Report Charges"
        }
        # response = requests.post(api_url, json=request, headers=headers)
        response = requests.post(api_url, json=request_data, headers=headers)
        print(response)
    return HttpResponse("Payment Successfull")

@login_required
def stk(request):
    return render(request, 'pay.html')

@csrf_exempt
def callback(request):
    if request.method != "POST":
        return HttpResponse("Invalid Request")
    # else:
    try:
        callback_data = json.loads(request.body)
        print(callback_data)
        user = request.user
        result_code = callback_data["Body"]["stkCallback"]["ResultCode"]
        if result_code != "0":
            error_message = callback_data["Body"]["stkCallback"]["ResultDesc"]
            return JsonResponse({"result_code": result_code, "ResultDesc": error_message})

        # merchant_id = callback_data["Body"]["stkCallback"]["MerchantRequestID"]
        checkout_id = callback_data["Body"]["stkCallback"]["CheckoutRequestID"]
        body = callback_data["Body"]["stkCallback"]["CallbackMetadata"]["Item"]

        amount = next(item["Value"] for item in body if item["Name"] == "Amount")
        mpesa_code = next(item["Value"] for item in body if item["Name"] == "MpesaReceiptNumber")
        phone_number = next(item["Value"] for item in body if item["Name"] == "PhoneNumber")

        trans=Transactions(user=user, amount=amount, mpesa_code=mpesa_code, phone_number=phone_number,
                                    checkout_id=checkout_id, status="Success")
        trans.save()
        response_data = {"message": "success",
                         "trans": {
                             "user": str(trans.user),
                             "amount": trans.amount,
                             "mpesa_code": trans.mpesa_code,
                             "phone_number": trans.phone_number,
                             "checkout_id": trans.checkout_id,
                             "status": trans.status}}
        return JsonResponse(response_data, safe=False)
    except (json.JSONDecodeError, KeyError) as e:
        return HttpResponse(f"Invalid Request: {str(e)}")


