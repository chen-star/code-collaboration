from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls import url

from django.contrib.auth.views import LoginView,LogoutView
from codereviewer import views,forms
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^settings/?$', views.settings, name='settings'),
    url(r'^repositories/?$', views.repositories, name='repo'),
    url(r'^review/?$', views.review, name='review'),#to be deleted
    # url(r'^review/(?P<project_id>.+)/(?P<file_name>.+)$', views.review, name='review'),
    url(r'^registration/?$', views.registration, name='registration'),
]
