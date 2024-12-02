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
    path('reportview/', views.report_view, name='reportview')
    # path('activityupdate/<int:id>', views.activityupdate, name='activityupdate'),
    # path('issueupdate/<int:id>/', views.issueupdate, name='issueupdate'),
]