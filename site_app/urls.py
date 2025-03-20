from django.urls import path
from . import views

urlpatterns= [
    path('', views.index, name='index'),
    path('login/', views.log_in, name='login'),
    path('signup/', views.sign_up, name='signup'),

    path('delete/<int:id>/', views.deleteData, name="deleteData"),
    path('dashboard/', views.dash, name='dash'),

    path('dashboard/sites-in-progress/', views.site_in_progress_view, name='sites-in-progress'),
    path('dashboard/activitylog/', views.activitylog, name='activitylog'),
    path('dashboard/activityview/', views.activityview, name='activityview'),

    path('dashboard/view-profile/', views.user_profile_view, name='view-profile'),
    path('dashboard/subscriptions/', views.subscription_view, name='subscriptions'),

    path('dashboard/issuelog/', views.issuelog, name='issuelog'),
    path('dashboard/issueview/', views.issueview, name='issueview'),

    path('dashboard/activityreport/', views.activity_report, name='activityrep'),
    path('dashboard/issuereport/', views.issue_report, name='issuerep'),

    path('dashboard/activityreportdisplay/<int:id>/', views.activity_report_display, name='activityreportdisplay'),
    path('dashboard/issuereportdisplay/<int:id>/', views.issue_display, name='issuereportdisplay'),

    path('token/', views.token, name='token'),
    # path('pay/', views.pay, name='pay'),
    path('callback/', views.pay, name='pay'),
    path('stk/', views.stk, name='stk'),

    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    # path('callback/', views.callback, name='callback'),
]
