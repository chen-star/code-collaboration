from django import forms
from codereviewer.models import *

class CreateRepoForm(forms.ModelForm):	
	class Meta:
		model = Repo
		fields = ['project_name', 'files']
		widgets = {'files': forms.FileInput()}