from django.contrib import auth
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import ensure_csrf_cookie

from codereviewer.models import *
from codereviewer.forms import *

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from codereviewer.tokens import account_activation_token


def index(request):
    context={}
    user = request.user

    return render(request,'codereviewer/home.html',context)


def settings(request):
    context={}
    return render(request,'codereviewer/settings.html',context)


def repositories(request):    
    context = {}
    errors = []
    if request.method == 'POST':    	
    	form = CreateRepoForm(request.POST, request.FILES)
    	if form.is_valid():
    		new_repo = form.save()
    		return render(request, 'codereviewer/repo.html', context)    
    context['form'] = CreateRepoForm()
    return render(request, 'codereviewer/repo.html', context)


def review(request):
    context={}
    return render(request,'codereviewer/review.html',context)


# handle user registration
@transaction.atomic
@ensure_csrf_cookie
def registration(request):
    context = {}

    if request.method == 'GET':
        context['form'] = DeveloperRegForm()
        return render(request, 'codereviewer/registration.html', context)

    form = DeveloperRegForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request, 'codereviewer/registration.html', context)

    new_user = User.objects.create_user(username=form.cleaned_data['user_name'],
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])

    new_developer = Developer(user_name=form.cleaned_data['user_name'],
                              first_name=form.cleaned_data['first_name'],
                              last_name=form.cleaned_data['last_name'],
                              email=form.cleaned_data['email'],
                              password=form.cleaned_data['password'],
                              company=form.cleaned_data['company'],
                              department=form.cleaned_data['department'],
                              group=form.cleaned_data['group'],
                              title=form.cleaned_data['title'])

    new_user.save()
    new_developer.save()
    new_user.is_active = False

    return confirm_email(request, new_developer)


# email confirmation when registration
def confirm_email(request, new_user):
    sbj = 'Code Viewer Registration Confirmation'
    msg = render_to_string('codereviewer/fakeEmail.html', {
                'user': new_user,
                'domain': "127.0.0.1:8000",
                'uid': urlsafe_base64_encode(force_bytes(new_user.pk)).decode(),
                'token': account_activation_token.make_token(new_user),
            })
    send_mail([new_user.email], sbj, msg)
    return HttpResponse("Please confirm your email address to complete the registration!", content_type='text/plain')


# send email helper function
def send_email(address, sbj, msg):
    send_mail(subject=sbj, message=msg, from_email="coderviewerTeam@andrew.cmu.edu", recipient_list=address)


# activate account
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        auth.login(request, user)
        return redirect(reverse('codereviewer/repo.html'))
    else:
        return HttpResponse('Activation link is invalid!', content_type='text/plain')




