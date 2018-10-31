from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

def index(request):
    context={}
    user = request.user

    return render(request,'codereviewer/home.html',context)

def settings(request):
    context={}
    return render(request,'codereviewer/settings.html',context)

def repositories(request):
    context={}
    return render(request,'codereviewer/repo.html',context)

def review(request):
    context={}
    return render(request,'codereviewer/review.html',context)
