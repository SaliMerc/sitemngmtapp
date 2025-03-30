from datetime import datetime
import uuid
from django.contrib.sites import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password
from django.contrib.auth import update_session_auth_hash

# from .models import ....
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import pytz

from SiteLogger import settings
from site_app.models import OTP, DailyActivity, Issue, Image, Document, IssuePhoto, ActivityReport, IssueReport, Transactions, Subscription,SubscriptionAmount
from django.utils.timezone import now
from datetime import date
from django.template.loader import get_template
from requests.auth import HTTPBasicAuth
import json
from . credentials import MpesaAccessToken, LipanaMpesaPassword,MpesaC2bCredential
import requests

# for emails
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.contrib.staticfiles.storage import staticfiles_storage
import os
from django.conf import settings

from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, redirect

from django.db.models import Count, Q


def sign_up(request):
    if request.method == "POST":
        try:
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

            # otp verification begins here
            registration_data = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'password': password,
                }

            my_session_id = str(uuid.uuid4())
            request.session['id'] = my_session_id
            request.session['registration_info'] = registration_data
            request.session.set_expiry(900)

            otp = OTP.objects.create(session_id=my_session_id)
            otp.save()
            otp.generate_otp()

            subject = 'Email Verification'
                
            html_content = render_to_string('otp-verification-email.html', {
                'name': first_name,
                'otp': otp.code,
                })
            
            text_content = strip_tags(html_content)
            registration_email = EmailMultiAlternatives(subject, text_content, to=[email])
            registration_email.attach_alternative(html_content, "text/html")
            
            registration_email.send()

            messages.info(request, f'Enter the OTP code sent to {email} to activate your account') 

            # myuser = User.objects.create_user(username=email, email=email, password=password, first_name=first_name, last_name=last_name)
            # myuser.save()
            initial_url = reverse('verification')
            next_url = f"{initial_url}?next={reverse('login')}"
            return redirect(next_url)

            return redirect('login')
        except Exception as e:
            print(e)
    return render(request, 'signup.html')

def otp_verification(request):
    try:
        registration_user = request.session['registration_info']
    except KeyError:
        # if the session has expired
        messages.error(request, "Session ended, please register")
        return redirect('signup')
    
    if request.method == 'POST':
        try:
            code=request.POST.get("otp")
            otp = OTP.objects.get(session_id=request.session['id'])
            if not otp or not otp.is_valid:
                if otp:
                    # if otp has expired
                    otp.delete()
                new_otp = OTP.objects.create(session_id=request.session['id'])
                new_otp.save()
                new_otp.generate_otp()

                subject = 'Email Verification'
                
                html_content = render_to_string('otp-verification-email.html', {
                    'name': registration_user['first_name'],
                    'otp': new_otp.code,
                    })
                
                text_content = strip_tags(html_content)
                
                email = EmailMultiAlternatives(subject, text_content, to=[registration_user['email']])
                email.attach_alternative(html_content, "text/html")
                
                email.send()

                messages.info(request, f"Enter the OTP code sent to {registration_user['email']} to activate your account")
                return redirect('verify')
            if otp and otp.code == code:
                myuser = User.objects.create_user(
                    username=registration_user['email'], 
                    email=registration_user['email'], 
                    first_name=registration_user['first_name'], 
                    last_name=registration_user['last_name']
                    )
                
                myuser.set_password(registration_user['password'])
                myuser.save()
                otp.delete()

                request.session['id'] = None
                request.session['registration_info'] = None

                messages.success(request, 'OTP verification successfull')

                # letting the user know that their email has been verified successfully
                subject = 'Welcome to SiteLogger'
                
                html_content = render_to_string('otp-confirmation-email.html', {
                    'name': myuser.last_name,
                    })
                
                text_content = strip_tags(html_content)
                
                email = EmailMultiAlternatives(subject, text_content, to=[registration_user['email']])
                email.attach_alternative(html_content, "text/html")
                
                email.send()

                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('login')
            else:
                messages.success(request, 'Incorrect OTP, Try again')
            
        except Exception as e:
            print(e)
            messages.error(request, 'An error was encountered while submitting the code, try again')
            return redirect('verification')

    return render(request, 'otp-verification-page.html')

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


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "User account does not exist, create one")
            return redirect('signup')
        else:
            # for sending the password reset link
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            reset_link = f"{request.scheme}://{request.get_host()}/reset/{uid}/{token}/"
            subject = 'Password Reset Link'

            html_content = render_to_string('password-reset-email.html', {
                'user': user,
                'reset_link': reset_link,
            })

            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(subject, text_content, to=[user.email])
            email.attach_alternative(html_content, "text/html")

            email.send()

            messages.info(request, "A reset link has been sent to your email")
            return redirect('forgot_password')
    else:
        return render(request, 'forgot_password.html')


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Validating the token
    if not user or not default_token_generator.check_token(user, token):
        messages.error(request, "Invalid or expired link. Please request a new link")
        return redirect("forgot_password")

    if request.method == "POST":
        try:
            new_password = request.POST.get("n-password")
            confirm_password = request.POST.get("confirm-n-password")

            if new_password != confirm_password:
                messages.error(request, "New passwords don't match")

            elif check_password(new_password, user.password):
                messages.error(request, "New password cannot be same as the old password")

            else:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Your password has been changed successfully!, Login")
                return redirect("login")
        except Exception as e:
            messages.error(request, "Password Reset Failed")
            print(e)

    return render(request, 'password-reset-page.html', { 'uid': uidb64,
        'token': token})

def redirected_page(request):
    return render(request, "password-reset-page.html")

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
        user=request.user
        sites = DailyActivity.objects.filter(user=user).exclude(construction_stage='handover').values('site_name').distinct()
        count=sites.count()
        sites_in_progress = DailyActivity.objects.filter(user=user).exclude(construction_stage='handover').values('site_name').distinct()[:6]
        return render(request, 'dash.html', {'user':user, "sites_in_progress":sites_in_progress,"count":count})
    else:
        return redirect('login')

@login_required
def site_in_progress_view(request):
    if request.user.is_authenticated:
        user=request.user
        sites = DailyActivity.objects.filter(user=user,in_trash=False).exclude(construction_stage='handover').values('site_name').distinct()
        count=sites.count()
        sites_in_progress = DailyActivity.objects.filter(user=user,in_trash=False).exclude(construction_stage='handover').values('site_name').distinct()[:6]
        return render(request, 'sites-in-progress.html', {'user':user, "sites_in_progress":sites_in_progress,"count":count})

@login_required
def user_profile_view(request):
    if request.user.is_authenticated:
        user = request.user
        subscription=Subscription.objects.filter(user=user)
        subscription_amount=SubscriptionAmount.objects.first()
        return render(request, 'view-user-profile.html', {'user':user, "subscription":subscription, "subscription_amount":subscription_amount})
@login_required
def subscription_view(request):
    if request.user.is_authenticated:
        subscription_amount=SubscriptionAmount.objects.first()
        return render(request, 'subscriptions.html', {"subscription_amount":subscription_amount})


@login_required
def activitylog(request):
    construction_stage=DailyActivity.STAGE_CHOICES
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
        construction_stage = request.POST.get("construction_stage")
        images=request.FILES.getlist("images")
        documents=request.FILES.getlist("docs")
        user = request.user
        activity=DailyActivity(date=date, site_open_time=site_open_time, site_close_time=site_close_time, work_completed=work_completed, equipment_used=equipment_used, materials_used=materials_used,site_name=site_name,site_type=site_type,user=user,construction_stage=construction_stage)
        activity.save()
        for image in images:
            img = Image.objects.create(image=image, user=user)
            activity.progress_photos.add(img)

        for document in documents:
            doc = Document.objects.create(document=document, user=user)
            activity.relevant_documents.add(doc)
        activity.save()
        return redirect("activityview")
    existing_sites = DailyActivity.objects.filter(user=request.user).values_list("site_name", flat=True).distinct().order_by("site_name")
    return render(request, 'activitylog.html', {"existing_sites":existing_sites, "last_name":last_name,"construction_stage":construction_stage})


@login_required
def activityview(request):
    if request.user.is_authenticated:
        last_name = request.user.last_name
    query=request.GET.get("search",'').strip()
    activities=DailyActivity.objects.filter(user=request.user, in_trash=False).order_by("-date")
    if query:
        activities=DailyActivity.objects.filter(Q(site_name__icontains=query)|Q(work_completed__icontains=query)|Q(equipment_used__icontains=query)|Q(materials_used__icontains=query)|Q(construction_stage__icontains=query)|Q(date__icontains=query),user=request.user, in_trash=False).order_by("-date")
    return render(request, 'activityview.html',{'activities':activities, "last_name":last_name})
@login_required
def issuelog(request):
    issue_status=Issue.STATUS_CHOICES
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
    existing_sites = Issue.objects.filter(user=request.user).values_list("site_name",flat=True).distinct().order_by("site_name")
    return render(request, 'issuelog.html', {"existing_sites":existing_sites, "last_name":last_name,"issue_status":issue_status})
@login_required
def issueview(request):
    if request.user.is_authenticated:
        last_name = request.user.last_name

    query = request.GET.get("search", '').strip()
    issues=Issue.objects.filter(user=request.user,in_trash=False).order_by('-issue_date')
    if query:
        issues = Issue.objects.filter(
            Q(site_name__icontains=query) | Q(issue_description__icontains=query) | Q(resolution_steps__icontains=query) | Q(
                issue_status__icontains=query)| Q(issue_date__icontains=query),
            user=request.user, in_trash=False).order_by("-issue_date")
    return render(request, 'issueview.html', {'issues':issues, "last_name":last_name})

@login_required
def issueupdate(request,id):
    my_issue=get_object_or_404(Issue,id=id)
    issue_status = Issue.STATUS_CHOICES
    if request.method == "POST":
        try:
            my_issue.issue_date = request.POST.get("issue_date")
            my_issue.issue_time = request.POST.get("issue_time")
            my_issue.issue_description = request.POST.get("issue_description")
            my_issue.resolution_steps = request.POST.get("resolution_steps")
            my_issue.issue_status = request.POST.get("issue_status")
            my_issue.site_name = request.POST.get("site_name")

            my_issue.save()
            return redirect('issueview')
            messages.error(request, "Issue updated successfully")
        except Exception as e:
            print(e)
            messages.error(request, "Issue update failed")

    existing_sites = Issue.objects.filter(user=request.user).values_list("site_name", flat=True).distinct().order_by(
        "site_name")
    return render(request, 'issueupdate.html',
                  {"existing_sites": existing_sites, "issue_status": issue_status,"my_issue": my_issue})

@login_required()
def delete_issue(request, id):
    issue=get_object_or_404(Issue, id=id)
    issue.delete()
    return redirect("issueview")

@login_required
def activityupdate(request, id):
    construction_stage = DailyActivity.STAGE_CHOICES
    my_activity=get_object_or_404(DailyActivity, id=id)
    if request.method == "POST":
        try:
            my_activity.date = request.POST.get("date")
            my_activity.site_open_time = request.POST.get("open-time")
            my_activity.site_close_time = request.POST.get("close-time")
            my_activity.work_completed = request.POST.get("work-completed")
            my_activity.equipment_used = request.POST.get("equipment-used")
            my_activity.materials_used = request.POST.get("material-used")
            my_activity.site_name = request.POST.get("site_name")
            my_activity.construction_stage = request.POST.get("construction_stage")

            my_activity.save()
            return redirect('activityview')
            messages.success(request, "Activity updated successfully")
        except Exception as e:
            print(e)
            messages.error(request, "Activity update failed")

    existing_sites = DailyActivity.objects.filter(user=request.user).values_list("site_name",
                                                                                 flat=True).distinct().order_by("site_name")
    return render(request, 'activityupdate.html',
                  {"existing_sites": existing_sites, "construction_stage": construction_stage,"my_activity": my_activity})
@login_required()
def delete_activity(request, id):
    activity=get_object_or_404(DailyActivity, id=id)
    activity.delete()
    return redirect("activityview")

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
    activities = DailyActivity.objects.filter(user=user, site_name=site_name,in_trash=False).order_by("-date")

    filter_type = request.GET.get("report_type")
    one_day_query=request.GET.get("a-date")
    start_day = request.GET.get("start-date")
    end_day = request.GET.get("end-date")

    if filter_type=='one-day':
        activities = DailyActivity.objects.filter(date__icontains=one_day_query,user=user, site_name=site_name, in_trash=False).order_by("-date")
    elif filter_type=='multiple-days':
        start_date = datetime.strptime(start_day, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_day, '%Y-%m-%d').date()
        if start_date <= end_date:
            activities = DailyActivity.objects.filter(date__range=[start_date, end_date], user=user, site_name=site_name,in_trash=False).order_by("-date")
        else:
            activities=None
            messages.error(request, "Start Day should be earlier than the End Day")

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
    issue_new=Issue.objects.filter(user=user, site_name=site_name,in_trash=False).order_by("issue_date")

    filter_type = request.GET.get("report_type")
    one_day_query=request.GET.get("a-date")
    start_day = request.GET.get("start-date")
    end_day = request.GET.get("end-date")

    if filter_type=='one-day':
        issue_new = Issue.objects.filter(issue_date__icontains=one_day_query,user=user, site_name=site_name, in_trash=False).order_by("-issue_date")
    elif filter_type=='multiple-days':
        start_date = datetime.strptime(start_day, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_day, '%Y-%m-%d').date()
        if start_date <= end_date:
            issue_new = Issue.objects.filter(issue_date__range=[start_date, end_date], user=user, site_name=site_name,in_trash=False).order_by("-issue_date")
        else:
            issue_new=None
            messages.error(request, "Start Day should be earlier than the End Day")

    return render(request, 'issue_report_display.html', {"user":user, "site_name":site_name, "issue_new":issue_new, "last_name":last_name})

@login_required
def edit_user_profile(request):
    user=request.user
    if request.method=='POST':
        try:
            user.first_name=request.POST.get("fname").strip()
            user.last_name=request.POST.get("lname").strip()
            user.email=request.POST.get("email").strip()

            user.save()
            messages.success(request, "Profile Updated Successfully")
        except Exception as e:
            print(f"The exception is {e}")
            messages.error(request, "Profile Update Failed")
    return render(request, 'edit-profile.html', {"user":user})

@login_required
def edit_password(request):
    user=request.user
    if request.method=='POST':
        try:
            old_password=request.POST.get("o-password")
            new_password = request.POST.get("n-password")
            confirm_password = request.POST.get("confirm-n-password")

            if not check_password(old_password, user.password):
                messages.error(request, "Old password is incorrect")
            elif new_password != confirm_password:
                messages.error(request, "New passwords don't match")
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed successfully!")
        except Exception as e:
            print(f"The exception is {e}")
            messages.error(request, "Profile Update Failed")
    return render(request, 'change-password.html', {"user":user})


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
        print(request_data)
    return HttpResponse("Check your phone for a payment popup")

@login_required
def stk(request):
    subscription_amount = SubscriptionAmount.objects.first()
    return render(request, 'pay.html', {'subscription_amount':subscription_amount})

@csrf_exempt
def callback(request):
    try:
        print("Raw request body:", request.body)
        print("Headers:", request.headers)

        # Handle text/plain content type
        content_type = request.headers.get('Content-Type', '')
        if 'application/json' not in content_type:
            # If content type is not JSON, assume it's text/plain and parse it as JSON
            callback_data = json.loads(request.body.decode('utf-8'))
        else:
            # If content type is JSON, parse it directly
            callback_data = json.loads(request.body.decode('utf-8'))
        # callback_data = json.loads(request.body)
        print(callback_data)
        user = request.user
        result_code = callback_data["Body"]["stkCallback"]["ResultCode"]
        if result_code != "0":
            error_message = callback_data["Body"]["stkCallback"]["ResultDesc"]
            return JsonResponse({"result_code": result_code, "ResultDesc": error_message})

        print(result_code)
        # merchant_id = callback_data["Body"]["stkCallback"]["MerchantRequestID"]
        checkout_id = callback_data["Body"]["stkCallback"]["CheckoutRequestID"]
        body = callback_data["Body"]["stkCallback"]["CallbackMetadata"]["Item"]

        amount = next(item["Value"] for item in body if item["Name"] == "Amount")
        mpesa_code = next(item["Value"] for item in body if item["Name"] == "MpesaReceiptNumber")
        phone_number = next(item["Value"] for item in body if item["Name"] == "PhoneNumber")

        print(amount, mpesa_code, phone_number)
        trans=Transactions(user=user, amount=amount, mpesa_code=mpesa_code, phone_number=phone_number,
                                    checkout_id=checkout_id, status="Success")
        trans.save()
        # response_data = {"message": "success",
        #                  "trans": {
        #                      "user": str(trans.user),
        #                      "amount": trans.amount,
        #                      "mpesa_code": trans.mpesa_code,
        #                      "phone_number": trans.phone_number,
        #                      "checkout_id": trans.checkout_id,
        #                      "status": trans.status}}
        # print(response_data)
        # return JsonResponse(response_data, safe=False)
    except (json.JSONDecodeError, KeyError) as e:
        return HttpResponse(f"Invalid Request: {str(e)}")



