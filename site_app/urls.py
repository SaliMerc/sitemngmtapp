from django.urls import path
from . import views

urlpatterns= [
    path('', views.index, name='index'),
    path('login/', views.log_in, name='login'),
    path('signup/', views.sign_up, name='signup'),
    path('delete/<int:id>/', views.deleteData, name="deleteData"),
    path('dash/', views.dash, name='dash'),
    path('activitylog/', views.activitylog, name='activitylog'),
    path('activityview/', views.activityview, name='activityview'),
    path('activityview/<int:id>/', views.activity_view, name='activityview'),
    path('issuelog/', views.issuelog, name='issuelog'),
    path('issueview/', views.issuelist, name='issueview'),
    path('issueview/<int:id>/', views.issueview, name='issueview'),
    path('activityreport/', views.activity_report, name='activityrep'),
    path('issuereport/', views.issue_report, name='issuerep'),
    path('activityreportdisplay/<int:id>/', views.activity_report_display, name='activityreportdisplay'),
    path('issuereportdisplay/<int:id>/', views.issue_display, name='issuereportdisplay'),
    path('token/', views.token, name='token'),
    path('pay/', views.pay, name='pay'),
    path('stk/', views.stk, name='stk'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('callback/', views.callback, name='callback'),
]
