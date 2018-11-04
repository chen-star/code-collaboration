from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
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
    context = {}
    user = request.user

    # if not request.user.is_authenticated:
    return render(request, 'codereviewer/home.html', context)

    msg = Developer.objects.get(user=user).receiver_msg.all.order_by('-time')
    print(msg)
    context['messages'] = msg

    return render(request, 'codereviewer/home.html', context)


def settings(request):
    context = {}
    return render(request, 'codereviewer/settings.html', context)


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
    context = {}
    return render(request, 'codereviewer/review.html', context)


# handle user registration
@transaction.atomic
@ensure_csrf_cookie
def registration(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('repo'))

    context = {}

    if request.method == 'GET':
        context['form'] = DeveloperRegForm()
        return render(request, 'codereviewer/registration.html', context)

    form = DeveloperRegForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        print(form.errors)
        context['err'] = form.non_field_errors()
        return render(request, 'codereviewer/registration.html', context)

    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password1'],
                                        email=form.cleaned_data['email'])
    new_user.first_name = form.cleaned_data['first_name']
    new_user.last_name = form.cleaned_data['last_name']
    new_user.is_active = False
    new_user.save()

    new_developer = Developer(user=new_user,
                              company=form.cleaned_data['company'],
                              department=form.cleaned_data['department'],
                              group=form.cleaned_data['group'],
                              title=form.cleaned_data['title'])
    new_developer.save()

    return confirm_email(request, new_user)


# email confirmation when registration
def confirm_email(request, new_user):
    sbj = 'Code Viewer Registration Confirmation'
    current_site = get_current_site(request)
    msg = render_to_string('codereviewer/registration_email.html', {
        'user': new_user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(new_user.pk)).decode(),
        'token': account_activation_token.make_token(new_user),
    })
    send_email([new_user.email], sbj, msg)
    return render(request, 'codereviewer/registration_done.html')


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
        user.developer.save()
        auth.login(request, user)
        return render(request, 'codereviewer/home.html')
    else:
        return render(request, 'codereviewer/registration_invalid.html')


# user login
@ensure_csrf_cookie
@transaction.atomic
def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('repo'))

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = auth.authenticate(username=username, password=password)
        user.is_active = True

        if user is not None and user.is_active:
            auth.login(request, user)
            return render(request, 'codereviewer/home.html')
        else:
            return HttpResponseRedirect(reverse('login'))

    else:
        return render(request, 'codereviewer/login.html')


# user logout
@ensure_csrf_cookie
@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")


# invite other to comment on a project
@transaction.atomic
@login_required
def invite(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('')

    # TODO: change receiver and project parameter name
    receiver_name = request.POST.get('receiver')
    receiver = Developer.objects.get(user__username=receiver_name)
    sender = request.user
    project_name = request.POST.get('project')
    project = Repo.objects.get(project_name=project_name)

    invitationMessage = InvitationMessage(receiver=receiver,
                                          sender=sender,
                                          project=project)
    print(invitationMessage)
    invitationMessage.save()

    # send invitation email to receiver
    invite_email(request, sender, receiver, project)


# email invitation
def invite_email(request, sender, receiver, project):
    sbj = 'Code Viewer Project Contribution Invitation'
    current_site = get_current_site(request)
    msg = render_to_string('codereviewer/invitation_email.html', {
        'sender': sender,
        'receiver': receiver,
        'project': project,
        'domain': current_site.domain,
    })
    send_email([receiver.email], sbj, msg)
    # TODO: change receiver parameter name
    return render(request, 'codereviewer/registration_done.html', {'receiver': receiver})
