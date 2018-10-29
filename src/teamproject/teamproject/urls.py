from django.contrib import admin
from django.urls import path, include, re_path

from django.contrib.auth.views import LoginView,LogoutView
from codereviewer import views,forms
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name = 'index'),
    
]
