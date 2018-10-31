from codereviewer.models import *
from codereviewer.forms import *

from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required



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
