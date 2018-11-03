from django import forms
from django.contrib.auth.forms import UserCreationForm

from codereviewer.models import *


# create repository form
class CreateRepoForm(forms.ModelForm):
    class Meta:
        model = Repo
        fields = ['project_name', 'files']
        widgets = {'files': forms.FileInput()}


# developer registration form
class DeveloperRegForm(forms.Form):
    username = forms.CharField(max_length=30,
                               label='Username',
                               widget=forms.TextInput())
    first_name = forms.CharField(max_length=30,
                                 label='First name',
                                 widget=forms.TextInput())
    last_name = forms.CharField(label='Last name',
                                widget=forms.TextInput())
    email = forms.EmailField(label='Email address',
                             widget=forms.TextInput())
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())
    company = forms.CharField(max_length=30, required=False)
    department = forms.CharField(max_length=30, required=False)
    group = forms.CharField(max_length=30, required=False)
    title = forms.CharField(max_length=20, required=False)

    #
    # class Meta:
    #     model = Developer
    #     fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'company',
    #               'department', 'group', 'title')

    def clean(self):
        super(DeveloperRegForm, self).clean()

    def clean_password(self):
        cleaned_data = super(DeveloperRegForm, self).clean()
        pw1 = cleaned_data.get('password1')
        pw2 = cleaned_data.get('password2')
        if not pw1 or not pw2 and pw1 != pw2:
            raise forms.ValidationError('Password and Password Confirmation did not match')

    def clean_user(self):
        cleaned_data = super(DeveloperRegForm, self).clean()
        username = cleaned_data.get('username')
        if User.objects.filter(username=username):
            raise forms.ValidationError('This username has already been taken')
        return username

    def clean_email(self):
        cleaned_data = super(DeveloperRegForm, self).clean()
        email = cleaned_data.get('email')
        if email and User.objects.filter(email=email):
            raise forms.ValidationError('This email address has already been taken')
        return email
