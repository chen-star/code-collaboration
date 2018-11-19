import urllib
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
import json
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt

from codereviewer.forms import *

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from codereviewer.tokens import account_activation_token, password_reset_token
import os
from github import Github
import base64
from urllib.request import *
from urllib.error import *
import django
import codereviewer


def index(request):
    context = {}
    user = request.user
    if not request.user.is_authenticated:
        return render(request, 'codereviewer/home.html', context)

    receiver = Developer.objects.get(user=user)
    messages = InvitationMessage.objects.filter(receiver=receiver).order_by('-time')
    print(messages)
    context['messages'] = messages
    return render(request, 'codereviewer/home.html', context)


# display the 'settings' view
@login_required
def settings(request):
    context = {}
    if request.method == 'GET':
        this_developer = Developer.objects.get(user=request.user)
        context['this_developer'] = this_developer

    return render(request, 'codereviewer/settings.html', context)


def edit_profile(request):
    context = {}
    if request.method == 'GET':
        developer = Developer.objects.get(user=request.user)
        context['this_developer'] = developer
        context['edit_flag'] = True
        context['form'] = UpdateProfileForm(initial={
            'company': developer.company,
            'department': developer.department,
            'group': developer.group,
            'title': developer.title})

    if request.method == 'POST':
        developer = Developer.objects.get(user=request.user)
        form = UpdateProfileForm(request.POST, request.FILES, instance=developer)
        if form.is_valid():
            form.save()
            return redirect(reverse('settings'))
        else:
            print("Eeeeeerror: not valid form")

    return render(request, 'codereviewer/edit_profile.html', context)


@login_required
def repositories(request):
    context = {}
    if request.method == 'GET':
        form = CreateRepoForm()
        context['form'] = form
        owning_repos = Repo.get_owning_repos(request.user).order_by('-modified_time')
        context['owning_repos'] = owning_repos

        membering_repos = Repo.get_membering_repos(request.user).order_by('-modified_time')
        context['membering_repos'] = membering_repos

    context['user'] = request.user
    return render(request, 'codereviewer/repo.html', context)


# create a new repository owned by the requesting user
@login_required
def create_repo(request):
    context = {}
    if request.method == 'POST':
        form = CreateRepoForm(request.POST, request.FILES)
        if form.is_valid():
            owner = Developer.objects.get(user=request.user)
            files = form.cleaned_data['file_name']
            project_name = form.cleaned_data['repo_name']
            modify_frequency = 0
            new_repo = Repo(owner=owner, project_name=project_name, modify_frequency=modify_frequency)
            new_repo.save()
            file_obj = File(file_name=files, repo=new_repo)
            file_obj.save()
            return redirect(reverse('repo'))
    context['form'] = CreateRepoForm()
    return redirect(reverse('repo'))


@login_required
def review(request, repo_id):
    context = {}
    # TODO check existance
    repo = Repo.objects.get(id=repo_id)
    # TODO current assume only one file in a repo
    file = File.objects.get(repo=repo)
    url = os.path.join(os.path.dirname(os.path.dirname(__file__)), file.file_name.url[1:])
    f = open(url, 'r')
    lines = f.read().splitlines()
    f.close()
    context['codes'] = lines
    context['repo'] = repo
    context['filename'] = file.file_name
    return render(request, 'codereviewer/review.html', context)


@login_required
def mark_read_then_review(request, repo_id):
    context = {}

    receiver = Developer.objects.get(user=request.user)
    project = Repo.objects.get(id=repo_id)

    message = InvitationMessage.objects.filter(receiver=receiver).filter(project=project)[0]
    message.is_read = True
    message.save()
    return render(request, reverse('review', kwargs={'repo_id': repo_id}), context)


def get_codes(request, repo_id):
    # TODO check existance
    repo = Repo.objects.get(id=repo_id)
    f = open(repo.files.url, 'r')
    lines = f.read().splitlines()
    context = {'codes': lines}
    return render(request, 'codereviewer/json/codes.json', context, content_type='application/json')


def get_comments(request, repo_id):
    # TODO check existance
    id = int(repo_id)
    repo = Repo.objects.get(id=id)
    file = File.objects.get(repo=repo)
    comments = Comment.objects.filter(file=file)
    context = {'comments': comments}
    return render(request, 'codereviewer/json/comments.json', context, content_type='application/json')


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
        return render(request, 'codereviewer/registration.html', context)

    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password1'], )
    new_user.email = form.cleaned_data['email']
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
        if not user:
            return render(request, 'codereviewer/login.html')
        user.is_active = True

        if user is not None and user.is_active:
            auth.login(request, user)
            return render(request, 'codereviewer/home.html')
        else:
            return HttpResponseRedirect(reverse('login'))

    else:
        return render(request, 'codereviewer/login.html')


# github login
@ensure_csrf_cookie
@transaction.atomic
def github_login(request):
    # define github account parameters
    GITHUB_CLIENTID = 'b352efbb6fad5e996f99'
    GITHUB_CLIENTSECRET = '9f250736e1483fe5ffa3c0db00605b83ec344e5d'
    GITHUB_CALLBACK = 'http://127.0.0.1:8000/codereviewer/github/'
    GITHUB_AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'

    data = {
        'client_id': GITHUB_CLIENTID,
        'client_secret': GITHUB_CLIENTSECRET,
        'redirect_uri': GITHUB_CALLBACK,
        'state': _get_refer_url(request),
    }
    github_auth_url = '%s?%s' % (GITHUB_AUTHORIZE_URL, urllib.parse.urlencode(data))
    return HttpResponseRedirect(github_auth_url)


def _get_refer_url(request):
    refer_url = request.META.get('HTTP_REFER',
                                 '/')
    host = request.META['HTTP_HOST']
    if refer_url.startswith('http') and host not in refer_url:
        refer_url = '/'
    return refer_url


# github auth
def github_auth(request):
    # define github account parameters
    GITHUB_CLIENTID = 'b352efbb6fad5e996f99'
    GITHUB_CLIENTSECRET = '9f250736e1483fe5ffa3c0db00605b83ec344e5d'
    GITHUB_CALLBACK = 'http://127.0.0.1:8000/codereviewer/github/'

    if 'code' not in request.GET:
        return redirect(reverse('index'))

    code = request.GET.get('code')

    url = 'https://github.com/login/oauth/access_token'
    data = {
        'grant_type': 'authorization_code',
        'client_id': GITHUB_CLIENTID,
        'client_secret': GITHUB_CLIENTSECRET,
        'code': code,
        'redirect_uri': GITHUB_CALLBACK,
    }

    data = urllib.parse.urlencode(data)
    binary_data = data.encode('utf-8')
    headers = {'Accept': 'application/json'}
    req = urllib.request.Request(url, binary_data, headers)
    response = urllib.request.urlopen(req)

    result = response.read()
    result = json.loads(result)
    access_token = result['access_token']

    url = 'https://api.github.com/user?access_token=%s' % (access_token)
    response = urllib.request.urlopen(url)
    html = response.read()
    html = html.decode('ascii')
    data = json.loads(html)
    username = data['name']
    password = 'admin'

    try:
        user1 = User.objects.get(username=username)
    except:
        user2 = User.objects.create_user(username=username,
                                         password=password)
        user2.save()
        new_developer = Developer(user=user2)
        new_developer.save()

    user = authenticate(username=username,
                        password=password)
    user.is_active = True
    auth.login(request, user)
    return HttpResponseRedirect(reverse('repo'))


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

    receiver_name = request.POST.get('receiver')
    receiver = Developer.objects.get(user__username=receiver_name)
    sender = Developer.objects.get(user=request.user)
    project_name = request.POST.get('project')
    project = Repo.objects.get(project_name=project_name)

    invitationMessage = InvitationMessage(receiver=receiver,
                                          sender=sender,
                                          project=project)
    print(invitationMessage)
    invitationMessage.save()

    # send invitation email to receiver
    invite_email(request, sender.user, receiver.user, project)

    return HttpResponseRedirect(reverse('repo'))
    # redirect(reverse('repo'))


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


@ensure_csrf_cookie
def resetpassword(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    if request.method == "GET":
        form = ResetForm()
        return render(request, 'codereviewer/password_reset_form.html', {'form': form})
    else:
        form = ResetForm(request.POST)
        if form.is_valid():
            email = request.POST.get('email', '')
            user = Developer.objects.get(user__email=email).user
            if Developer.objects.filter(user__email=email).exists():
                message = render_to_string('codereviewer/password_reset_link.html', {
                    'user': user,
                    'domain': "127.0.0.1:8000",
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                    'token': password_reset_token.make_token(user),
                })
                send_email([email], "Reset password", message)
                return render(request, 'codereviewer/password_reset_done.html')
            else:
                return render(request, 'codereviewer/password_reset_form.html', {'form': form, 'email_is_wrong': True})
        else:
            context = {'form': form, 'validate': form.non_field_errors()}
            return TemplateResponse(request, 'codereviewer/password_reset_form.html', context)


@ensure_csrf_cookie
def confirmpassword(request, uidb64, token):
    form = ResetpwdForm()
    try:
        uid = force_text(urlsafe_base64_decode())
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        return TemplateResponse(request, 'codereviewer/password_reset_confirm.html',
                                {'form': form, 'isValidLink': False})
    if password_reset_token.check_token(user, token):
        return render(request, 'codereviewer/password_reset_confirm.html', {'form': form, 'isValidLink': True})
    else:
        return HttpResponse('Activation link is invalid!')


@ensure_csrf_cookie
def confirmpassword_helper(request):
    email = request.POST.get('email', '')
    user = User.objects.get(email=email)
    if request.method == 'POST' and Developer.objects.filter(user__email=email).exists():
        form = ResetpwdForm(request.POST)
        if form.is_valid():
            user.set_password(request.POST.get('newpassword1'))
            user.save()
            return render(request, 'codereviewer/password_reset_complete.html')
        return render(request, 'codereviewer/password_reset_confirm.html',
                      {'form': form, 'validate': form.non_field_errors()})


@csrf_exempt
def get_repo_from_github(request):
    if request.method == 'GET':
        new_form = GithubGetRepoForm()
        return render(request, 'codereviewer/githubAccount.html', {'form': new_form})

    form = GithubGetRepoForm(request.POST)
    if form.is_valid():
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        repo = request.POST.get('repository', '')

        # log into github account
        try:
            github = Github(username, password)
            github_user = github.get_user()
            reposi = github_user.get_repo(repo)
            contents = reposi.get_contents("")
            download_url = contents[0].download_url
            file = create_github_file(download_url)
            # create models
            repo_model = create_repo_model(reposi)
            create_file_model(file, repo_model)

            while len(contents) > 1:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    contents.extend(reposi.get_contents(file_content.path))
                else:
                    print(base64_decode(file_content.content))
                    print(file_content.download_url)

        except:
            return redirect(reverse('repo'))

    return redirect(reverse('repo'))


def base64_decode(str):
    return base64.b64decode(str)


def create_github_file(download_url):
    java_file = urlopen(download_url)
    file_url = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media/sourcecode/' + download_url[download_url.rfind('/') + 1:])
    with open(file_url, 'wb') as output:
        output.write(java_file.read())
    input = open(file_url)
    return input


def create_file_model(file, repo):
    myFile = django.core.files.File(file)
    file_model = codereviewer.models.File()
    file_model.file_name = myFile
    file_model.repo = repo
    file_model.save()


def create_repo_model(repository):
    owner = User.objects.get(username=repository.owner.name)
    owner = Developer.objects.get(user=owner)
    repo = Repo(owner=owner, project_name=repository.name)
    repo.save()
    return repo
