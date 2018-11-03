from django import forms
from codereviewer.models import *


# create repository form
class CreateRepoForm(forms.ModelForm):
    class Meta:
        model = Repo
        fields = ['project_name', 'files']
        widgets = {'files': forms.FileInput()}


# developer registration form
class DeveloperRegForm(forms.ModelForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    company = forms.CharField(max_length=30, required=False)
    department = forms.CharField(max_length=30, required=False)
    group = forms.CharField(max_length=30, required=False)
    title = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'password', 'confirm_password', 'company', 'department', 'group', 'title')

    def clean(self):
        cleaned_data = super(DeveloperRegForm, self).clean()
        pw1 = cleaned_data.get('password')
        pw2 = cleaned_data.get('confirm_password')
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
