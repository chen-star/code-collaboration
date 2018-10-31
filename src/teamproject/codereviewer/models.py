from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User


# Data model of project repository.
class Repo(models.Model):	
	owner = models.ForeignKey(User, related_name='owner', on_delete=models.CASCADE)	
	members =  models.ManyToManyField(User, related_name='members',blank=True)	
	files = models.FileField(upload_to='sourcecode', blank=True)
	project_name = models.CharField(max_length=128, blank=False)
	create_time = models.DateTimeField(auto_now_add=True)
	modified_time = models.DateTimeField(auto_now=True)
	modify_frequency = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])	

	def __unicode__(self):
		return self.project_name

	def __str__(self):
		return self.__unicode__()