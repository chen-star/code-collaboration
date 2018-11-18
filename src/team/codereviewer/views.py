import urllib
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import ensure_csrf_cookie

from codereviewer.models import *
from codereviewer.forms import *

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from codereviewer.tokens import account_activation_token, password_reset_token
import os


def index(request):
    context = {}
    user = request.user

    # if not request.user.is_authenticated:
    return render(request, 'codereviewer/home.html', context)
    # TODO: change user state
    msg = Developer.objects.get(user=user).receiver_msg.all.order_by('-time')
    print(msg)
    context['messages'] = msg

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
        owning_repos = Repo.get_owning_repos(request.user)
        context['owning_repos'] = owning_repos

        membering_repos = Repo.get_membering_repos(request.user)
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
            files = form.cleaned_data['files']
            project_name = form.cleaned_data['project_name']
            modify_frequency = 0
            new_repo = Repo(owner=owner, files=files, project_name=project_name, modify_frequency=modify_frequency)
            new_repo.save()
            return redirect(reverse('repo'))
    context['form'] = CreateRepoForm()
    return redirect(reverse('repo'))


@login_required
def review(request, repo_id):
    context = {}
    # TODO check existance
    repo = Repo.objects.get(id=repo_id)
    url = os.path.join(os.path.dirname(os.path.dirname(__file__)), repo.files.url[1:])
    f = open(url, 'r')
    lines = f.read().splitlines()
    f.close()
    context['codes'] = lines
    context['repo'] = repo
    context['filename'] = repo.files
    return render(request, 'codereviewer/review.html', context)


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
    comments = Comment.objects.filter(file=repo)
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
    GITHUB_CLIENTSECRET = '9f250736e1483fe5ffa3c0db00605b83ec344e5dt'
    GITHUB_CALLBACK = 'http://127.0.0.1:8000/codereviewer/repositories'
    GITHUB_AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'

    data = {
        'client_id': GITHUB_CLIENTID,
        'client_secret': GITHUB_CLIENTSECRET,
        'redirect_uri': GITHUB_CALLBACK,
        'state': _get_refer_url(request),
    }
    github_auth_url = '%s?%s' % (GITHUB_AUTHORIZE_URL, urllib.parse.urlencode(data))
    print('git_hub_auth_url', github_auth_url)
    return HttpResponseRedirect(github_auth_url)

def _get_refer_url(request):
    refer_url = request.META.get('HTTP_REFER',
                                 '/')
    host = request.META['HTTP_HOST']
    if refer_url.startswith('http') and host not in refer_url:
        refer_url = '/'
    return refer_url

#
# # github auth
# def github_auth(request):
#     template_html = 'account/login.html'
#
#     # 如果申请登陆页面成功后，就会返回code和state(被坑了好久)
#     if 'code' not in request.GET:
#         return render(request,template_html)
#
#     code = request.GET.get('code')
#
#     # 第二步
#     # 将得到的code，通过下面的url请求得到access_token
#     url = 'https://github.com/login/oauth/access_token'
#     data = {
#         'grant_type': 'authorization_code',
#         'client_id': GITHUB_CLIENTID,
#         'client_secret': GITHUB_CLIENTSECRET,
#         'code': code,
#         'redirect_uri': GITHUB_CALLBACK,
#     }
#
#     data = urllib.parse.urlencode(data)
#
#     # 请求参数需要bytes类型
#     binary_data = data.encode('utf-8')
#     print('data:', data)
#
#     # 设置请求返回的数据类型
#     headers={'Accept': 'application/json'}
#     req = urllib.request.Request(url, binary_data,headers)
#     print('req:', req)
#     response = urllib.request.urlopen(req)
#
#     # json是str类型的，将bytes转成str
#     result = result.decode('ascii')
#     result = json.loads(result)
#     access_token = result['access_token']
#     # print('access_token:', access_token)
#
#     url = 'https://api.github.com/user?access_token=%s'
#      % (access_token)
#     response = urllib.request.urlopen(url)
#     html = response.read()
#     html = html.decode('ascii')
#     data = json.loads(html)
#     username = data['name']
#     # print('username:', username)
#     password = '111111'
#
#     # 如果不存在username，则创建
#     try:
#         user1 = User.objects.get(username=username)
#     except:
#         user2 = User.objects.create_user(username=username,
#         password=password)
#         user2.save()
#         profile = Profile.objects.create(user=user2)
#         profile.save()
#
#     # 登陆认证
#     user = authenticate(username=username,
#     password=password)
#     login(request, user)
#     return HttpResponseRedirect(reverse('index'))


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
