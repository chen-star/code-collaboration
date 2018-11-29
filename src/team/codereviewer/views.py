import base64
import datetime as dt
import json
import os
import re
import shutil
import urllib
import zipfile
from urllib.request import *

import django
from django.conf import settings as django_settings
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from github import Github
from datetime import datetime, timezone

import codereviewer
from codereviewer.forms import *
from codereviewer.tokens import account_activation_token, password_reset_token


def index(request):
    context = {}
    user = request.user
    if not request.user.is_authenticated:
        return render(request, 'codereviewer/home.html', context)
    context['user']=user
    receiver = Developer.objects.get(user=user)
    messages = InvitationMessage.objects.filter(receiver=receiver).order_by('-time')
    context['messages'] = messages
    new_reply_messages = NewReplyMessage.objects.filter(new_reply_receiver=receiver).order_by('-time')
    context['new_reply_messages'] = new_reply_messages
    return render(request, 'codereviewer/home.html', context)


# display the 'settings' view
@login_required
def settings(request):
    context = {}
    if request.method == 'GET':
        user = request.user
        username = user.developer
        this_developer = Developer.objects.get(user=user)
        cur = django.utils.timezone.now()

        userAct = User.objects.get(developer=username)
        last_login = dt.datetime.combine(userAct.last_login.date(),
                                               dt.time(userAct.last_login.hour, userAct.last_login.minute))

        numOfRepo = Repo.objects.filter(owner=username).count()
        repoTrend = Repo.objects.filter(owner=username, create_time__gte=cur - dt.timedelta(days=7)).count()
        numOfCom = Comment.objects.filter(commenter=this_developer).count()
        comTrend = Comment.objects.filter(commenter=this_developer,
                                          comment_time__gte=cur - dt.timedelta(days=7)).count()
        context['this_developer'] = this_developer
        context['active'] = last_login.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime('%Y-%m-%d %H:%M:%S')
        context['repos'] = numOfRepo
        context['repoTrend'] = repoTrend
        context['comments'] = numOfCom
        context['comTrend'] = comTrend

    return render(request, 'codereviewer/settings.html', context)


@login_required
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
            print("Error: not valid form")

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
        all_repos = owning_repos | membering_repos
        files_per_repo = []
        for repo in all_repos:
            this_repo = []
            all_files = File.objects.filter(repo=repo).order_by('file_name')
            this_repo = list(all_files)
            files_per_repo.append(this_repo)

        context['all_repos'] = all_repos
        context['files_per_repo'] = files_per_repo

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

            # handle a zip file or a single file.
            uploaded_file = files
            if not uploaded_file.name.endswith('.zip'):
                file_obj = File()
                file_obj.file_name = uploaded_file
                file_obj.file_name.name = str(owner.user.id) + '__' + str(new_repo.id) + '__' + uploaded_file.name
                file_obj.repo = new_repo
                file_obj.save()
            else:
                # create a tmp directory for unzipping.
                try:
                    os.mkdir(os.path.join(django_settings.BASE_DIR, 'tmp'))
                except:
                    pass

                # write the file to the tmp directory.
                full_filename = os.path.join(django_settings.BASE_DIR, 'tmp', uploaded_file.name)
                fout = open(full_filename, 'wb+')
                for chunk in uploaded_file.chunks():
                    fout.write(chunk)
                fout.close()

                # unzip the file and save them.
                save_zip(full_filename, owner.user.id, new_repo)
            # file upload ends.
            return redirect(reverse('repo'))

    context['form'] = CreateRepoForm()
    return redirect(reverse('repo'))


@login_required
def review(request, file_id):
    context = {}
    try:
        file = File.objects.get(id=file_id)
    except File.DoesNotExist:
        return render(request, 'codereviewer/NotFound.html', {'error': "Please make sure you've entered a correct filename"})
    # get the repo and check if current user has permission
    repo = file.repo
    if not (repo in Repo.get_membering_repos(request.user) or repo in Repo.get_owning_repos(request.user)):
        return render(request, 'codereviewer/NotFound.html', {'error': "You do not have permission to this file."})
    furl = ''
    if file.from_github:
        # url = file.file_name.name
        furl = os.path.dirname(os.path.dirname(__file__)) + file.file_name.url
    else:
        furl = os.path.join(os.path.dirname(os.path.dirname(__file__)), file.file_name.url[1:])
    f = open(furl, 'r')
    lines = f.read().splitlines()
    f.close()
    context['codes'] = lines
    context['repo'] = file.repo
    context['filename'] = file.file_name
    return render(request, 'codereviewer/review.html', context)


@login_required
def review_repo(request, repo_id):
    context = {}
    # If repo not exists, return Http404.
    try:
        repo = Repo.objects.get(id=repo_id)
    except Repo.DoesNotExist:
        return render(request, reverse('404'), context)

    # Serve the first file in the repo to user.
    # User may browse the whole repo once she gets into the repo.
    file = File.objects.filter(repo=repo)[0]
    return redirect(reverse('review', kwargs={'file_id': file.id}))


def add_comment(request):
    context = {}
    if request.method == 'POST':
        print("post comment")
        form = AddCommentForm(request.POST)
        if not form.is_valid():
            context['comment'] = []
            return render(request, 'codereviewer/json/comment.json', context, content_type='application/json')
        file = File.objects.get(id=request.POST.get('file_id'))
        new_comment = Comment(content=form.clean().get('commentcontent'),
                              commenter=Developer.get_developer(request.user)[0],
                              line_num=request.POST.get('line_num'))

        new_comment.save()
        file.comments.add(new_comment)
        context['comment'] = new_comment
    print("add comment")
    return render(request, 'codereviewer/json/comment.json', context, content_type='application/json')


def delete_comment(request):
    # check if the cmt exists
    cmt_to_delete = Comment.objects.filter(id=request.POST.get('comment_id'))
    if len(cmt_to_delete)>0:
        cmt_to_delete.delete
    return render(request, 'codereviewer/json/comment.json', {}, content_type='application/json')


def get_changed_comments(request, file_id, line_num, time):
    timestamp = dt.datetime.fromtimestamp(int(time) // 1000.0)  # convert
    file = File.objects.get(id=file_id)
    cmt = file.comments.all().filter(line_num=line_num)
    context = {
        'comments': Comment.objects.filter(id__in=cmt, comment_time__gt=timestamp).order_by('-comment_time').distinct(),
        'current_user': request.user}
    return render(request, 'codereviewer/json/comments.json', context, content_type='application/json')


def add_reply(request):
    context = {}
    if request.method == 'POST':
        form = AddReplyForm(request.POST)
        if not form.is_valid():
            context['reply'] = []
            return render(request, 'codereviewer/json/reply.json', context, content_type='application/json')
        new_reply = Reply(content=form.clean().get('replycontent'),
                          replier=Developer.get_developer(request.user)[0])

        new_reply.save()
        cmt = Comment.objects.get(id=request.POST.get('comment_id')[6:])
        cmt.reply.add(new_reply)
        context['reply'] = new_reply
    # messages.append("Successfully sent a comment!")
    return render(request, 'codereviewer/json/reply.json', context, content_type='application/json')


@login_required
def mark_read_then_review(request, msg_id):
    context = {}

    # Mark this message as read.
    message = InvitationMessage.objects.get(id=msg_id)
    message.is_read = True
    message.save()

    # To read this message means to accept the invitation of joining the repo.
    receiver = message.receiver
    repo = message.project
    repo.members.add(receiver)
    repo.save()

    return redirect(reverse('review_repo', kwargs={'repo_id': message.project.id}))

@login_required
def mark_read_then_review_new_reply(request, msg_id):
    context = {}
    # Mark this message as read.
    message = NewReplyMessage.objects.get(id=msg_id)
    message.is_read = True
    message.save()
    return redirect(reverse('review', kwargs={'file_id': message.file.id}))

@login_required
def get_codes(request, file_id):
    try:
        file = File.objects.get(id=file_id)
    except File.DoesNotExist:
        return render(request, 'codereviewer/NotFound.html', {'error': "Please make sure you've entered a correct filename"})

    file = File.objects.get(id=file_id)
    furl = ''
    if file.from_github:
        furl = os.path.dirname(os.path.dirname(__file__)) + file.file_name.url
    else:
        furl = os.path.join(os.path.dirname(os.path.dirname(__file__)), file.file_name.url[1:])
    print(furl)
    f = open(furl, 'r')
    lines = f.read().splitlines()
    for i in range(len(lines)):
        if lines[i].find('"') > -1:
            new_line = ""
            pass_flag = False
            for x in lines[i]:
                if pass_flag:
                    pass_flag = False
                    new_line = new_line + x
                    continue
                if x == '\\':
                    pass_flag = True
                if x == '"':
                    new_line = new_line + '\\'
                new_line = new_line + x
            lines[i] = new_line
        while lines[i].find('\t')>-1:
            lines[i] = lines[i][0:lines[i].find('\t')]+'    '+lines[i][lines[i].find('\t')+1:]
    digits = len(str(len(lines)))  # make up for display indent
    for d in range(1, digits):
        for i in range(int('1' + '0' * (d)) - 1):
            lines[i] = ' ' + lines[i]
    for i in range(len(lines)):
        lines[i] = ' ' + lines[i]
    context = {'codes': lines}
    context['commented_lines'] = set()
    all_comments = file.comments.all()
    if all_comments:
        for cmt in all_comments:
            context['commented_lines'].add(cmt.line_num)
    return render(request, 'codereviewer/json/codes.json', context, content_type='application/json')


def get_comments(request, file_id, line_num):
    # TODO check existance
    comments = Comment.get_comments(file_id, line_num)
    context = {'comments': comments, 'current_user': request.user}
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
            return HttpResponseRedirect(reverse('home'))
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
    receiver_set = Developer.objects.filter(user__username=receiver_name)
    if len(receiver_set)==0:
        return render(request, 'codereviewer/NotFound.html', {'error': "User "+receiver_name+" does not exist."})
    receiver = receiver_set[0]
    sender = Developer.objects.get(user=request.user)
    project_name = request.POST.get('project')
    project = Repo.objects.get(project_name=project_name)

    invitationMessage = InvitationMessage(receiver=receiver,
                                          sender=sender,
                                          project=project)
    invitationMessage.save()

    # send invitation email to receiver
    invite_email(request, sender.user, receiver.user, project)

    return HttpResponseRedirect(reverse('repo'))


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
    print(msg)
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


@login_required
@ensure_csrf_cookie
def search_bar(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        userobject = request.user
        owner = Developer.objects.get(user=userobject)
        user = Repo.objects.filter(owner=owner)
        results = []
        for repo in user:
            file = codereviewer.models.File.objects.get(repo=repo)
            url = os.path.join(os.path.dirname(os.path.dirname(__file__)), file.file_name.url[1:])
            filename = url[url.rfind('/') + 1:]
            if re.search(q, filename, re.IGNORECASE):
                result = str(repo.id) + ',' + url[url.rfind('/') + 1:]
                results.append(result)
        data = json.dumps(results)
        return HttpResponse(data, 'application/json')
    else:
        fileName = request.POST.get('fileSearch', '')
        tmp = str(fileName).split(",")
        fileID = tmp[0]
        print(fileID)
        if not id or not re.search('^[0-9]+,[0-9]+__[0-9]+__', str(fileName)):
            fileID = '-1'
            print(fileID)
        else:
            repo = Repo.objects.get(id=fileID)
            file = File.objects.filter(repo=repo)[0]
            fileID = file.id
            print(fileID)
        return redirect(reverse('review', kwargs={'file_id': fileID}))


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

            # no file in github repo
            if len(contents) == 0:
                return redirect(reverse('repo'))

            # only one file in github repo
            first_con = contents.pop(0)
            download_url = first_con.download_url
            fname = first_con.name
            file = create_github_file(download_url)
            # create models
            repo_model = create_repo_model(reposi)
            create_file_model(file, repo_model, fname)

            while len(contents) >= 1:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    contents.extend(reposi.get_contents(file_content.path))
                else:
                    download_url = file_content.download_url
                    fname = file_content.name
                    file = create_github_file(download_url)
                    # create models
                    create_file_model(file, repo_model, fname)

        except Exception as e:
            print(e)
            return redirect(reverse('repo'))

    return redirect(reverse('repo'))


def base64_decode(str):
    return base64.b64decode(str)


def create_github_file(download_url):
    code_file = urlopen(download_url)
    file_url = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            'media/sourcecode/' + download_url[download_url.rfind('/') + 1:])
    with open(file_url, 'wb') as output:
        output.write(code_file.read())
    input = open(file_url)
    return input


def create_file_model(file, repo, fname):
    myFile = django.core.files.File(file)
    user_id = repo.owner.user.id
    repo_id = repo.id
    file_model = codereviewer.models.File()
    file_model.file_name = myFile
    file_model.file_name.name = (str(user_id) + '/' + str(repo_id) + '/' + fname).replace('/', '__')
    file_model.from_github = True
    file_model.repo = repo
    file_model.save()


def create_repo_model(repository):
    owner = User.objects.get(username=repository.owner.name)
    owner = Developer.objects.get(user=owner)
    repo = Repo(owner=owner, project_name=repository.name)
    repo.save()
    return repo


# Unzip the uploaded zip file in place, and generate flattened file name
# Format like: some__path__name__filename
def unzip(file_name, store_dir, userid, repo):
    with open(file_name, 'rb') as file:
        zfile = zipfile.ZipFile(file)
        zfile.extractall(store_dir)

    # remove junk folder
    junkfolder = os.path.join(store_dir, '__MACOSX')
    shutil.rmtree(junkfolder)

    prefix = os.path.join(django_settings.MEDIA_ROOT, 'sourcecode')

    # recursively traverse, flatten files, and move them to sourcecode folder
    for root, dirs, files in os.walk(store_dir):
        for file_ in files:
            if file_ == '.DS_Store':
                continue

            # get the flattened file name like some__path__filename
            fname = os.path.join(root, file_)
            zipfile_len = len(file_name[-len(file_name.split('/')[-1]):].split('.')[0])

            tmp_flat_fname = str(userid) + '/' + str(repo.id) + fname[len(store_dir) + zipfile_len + 1:]
            flat_file_name = tmp_flat_fname.replace('/', '__')

            # move to media folder and save it as a Django object
            with open(fname, "r") as fh:
                myFile = django.core.files.File(fh)
                file_model = File()
                file_model.file_name = myFile
                file_model.file_name.name = flat_file_name
                file_model.repo = repo
                file_model.save()

    # remove temp folder and original zip file
    try:
        shutil.rmtree(store_dir)
        os.remove(file_name)
    except:
        pass


# Handle an uploaded zip file and save it in file system
def save_zip(file_name, userid, repo):
    store_dir = file_name.split('.')[0]
    unzip(file_name, store_dir, userid, repo)


def stat_console(request):
    return 0


def send_new_reply_msg(request):
    user = request.user
    replier = Developer.get_developer(user)[0]
    comment_id = request.POST.get('comment_id')[6:]
    file_id = request.POST.get('file_id')
    comment = Comment.objects.get(id=comment_id)
    receiver = comment.commenter
    if user.username == receiver.user.username:
        return render(request, 'codereviewer/json/reply.json', {}, content_type='application/json')

    file = File.objects.get(id=file_id)
    new_msg = NewReplyMessage(replier = replier,
                              new_reply_receiver = receiver,
                              file = file,
                              comment = comment)
    new_msg.save()
    return render(request, 'codereviewer/json/reply.json', {}, content_type='application/json')
