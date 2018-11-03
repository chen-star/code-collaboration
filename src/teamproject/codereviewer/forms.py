from django import forms
from codereviewer.models import *


# create repository form
class CreateRepoForm(forms.ModelForm):	
	class Meta:
		model = Repo
		fields = ['project_name', 'files']
		widgets = {'files': forms.FileInput()}


# developer registration form
class DeveloperRegForm(forms.Form):
	user_name = forms.CharField(max_length=20, label="User Name")
	first_name = models.CharField(max_length=50, label="First Name")
	last_name = models.CharField(max_length=20, label="Last Name")
	email = models.EmailField(max_length=40, label="Email Address", widget=forms.EmailInput())

	password = models.CharField(max_length=50, label="Password", widget=forms.PasswordInput())
	password_confirm = models.CharField(max_length=50, label="Password Confirmation", widget=forms.PasswordInput())

	company = models.CharField(max_length=30, required=False)
	department = models.CharField(max_length=30, required=False)
	group = models.CharField(max_length=30, required=False)
	title = models.CharField(max_length=20, required=False)

	def clean(self):
		super(DeveloperRegForm, self).clean()

	def clean_password(self):
		cleaned_data = super(DeveloperRegForm, self).clean()
		pw = cleaned_data.get('password')
		pw_confirm = cleaned_data.get('password_confirm')
		if pw and pw_confirm and pw != pw_confirm:
			raise forms.ValidationError('Password and Password Confirmation did not match')
		return pw

	def clean_user_name(self):
		cleaned_data = super(DeveloperRegForm, self).clean()
		user_name = cleaned_data.get('user_name')
		if user_name and Developer.objects.filter(user_name=user_name):
			raise forms.ValidationError('This username has already been taken')
		return user_name

	def clean_email(self):
		cleaned_data = super(DeveloperRegForm, self).clean()
		email = cleaned_data.get('email')
		if email and Developer.objects.filter(email=email):
			raise forms.ValidationError('This email address has already been taken')
		return email

	





