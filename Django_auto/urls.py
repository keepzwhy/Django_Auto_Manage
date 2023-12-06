"""
URL configuration for Django_auto project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from app01 import views

urlpatterns = [
    path('login/', views.login),
    path('logon/', views.logon),
    path('user/info/', views.user_info),
    path('user/edit/<str:username>/', views.user_edit, name='user_edit'),
    path('user/manager/', views.user_manage),
    path('server/info/', views.service_info),
    path('change/pwd/', views.change_pwd),
    path('show/after/', views.show_after),
    path('logout/', views.logout),
    path('service/user/edit/<str:name>/', views.service_user_edit, name='service_user_edit'),
    path('new/built/user/', views.new_built_user),
    path('monitor/cpu/', views.monitor_cpu),
    path('monitor/mem/', views.monitor_mem),
    path('process/manager/', views.process_manager)
]
