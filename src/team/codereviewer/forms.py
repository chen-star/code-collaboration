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
    company = forms.CharField(max_length=30, required=True)
    department = forms.CharField(max_length=30, required=True)
    group = forms.CharField(max_length=30, required=True)
    title = forms.CharField(max_length=20, required=True)

    def clean(self):
        cleaned_data = super(DeveloperRegForm, self).clean()
        pw1 = cleaned_data.get('password1')
        pw2 = cleaned_data.get('password2')
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError('Password and Password Confirmation did not match')

    def clean_username(self):
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


# developer profile updating form
class UpdateProfileForm(forms.ModelForm):         
    class Meta:
        model = Developer
        fields = ['company', 'department', 'group', 'title', 'avatar']
        widgets = {'avatar': forms.FileInput()}


class ResetForm(forms.Form):
    email = forms.EmailField(required=True, label="Email address", error_messages={'required': "enter email address"},
                             widget=forms.EmailInput(attrs={'rows': 1, 'cols': 20, }), )

    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError("Invalid email format, must ends with domain name")
        else:
            cleaned_data = super(ResetForm, self).clean()
        return cleaned_data


class ResetpwdForm(forms.Form):
    email = forms.EmailField(required=True, label="Email address", error_messages={'required': "enter email address"},
                             widget=forms.EmailInput(attrs={'rows': 1, 'cols': 20, }), )
    newpassword = forms.CharField(
        required=True,
        label="New password",
        error_messages={'required': "Enter your new password"},
        widget=forms.PasswordInput(
            attrs={'rows': 1, 'placeholder': "Length of password should be at least 5 chars"}), )

    confirmation = forms.CharField(
        required=True,
        label="Confirm password",
        error_messages={'required': 'Confirm your password'},
        widget=forms.PasswordInput(attrs={'rows': 1, 'placeholder': "Length of password should be at least 5 chars"}), )

    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError("All fields are required")
        elif len(self.cleaned_data['newpassword1']) < 5:
            raise forms.ValidationError("Password length should be at least 5")
        elif self.cleaned_data['newpassword1'] != self.cleaned_data['newpassword2']:
            raise forms.ValidationError("Your password and confirmation password do not match")
        else:
            cleaned_data = super(ResetpwdForm, self).clean()
        return cleaned_data
