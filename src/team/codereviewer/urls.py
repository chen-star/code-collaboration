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
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('invite', views.invite, name='invite'),
]
