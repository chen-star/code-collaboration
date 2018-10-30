from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

def index(request):
    context={}
    user = request.user

    return render(request,'home.html',context)

def settings(request):
    context={}
    return render(request,'settings.html',context)

def repositories(request):
    context={}
    return render(request,'repo.html',context)

def review(request,project_id,file_name):
    context={}
    return render(request,'review.html',context)
