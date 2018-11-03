from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User


# User login and registration model
class Developer(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
	company = models.CharField(max_length=30, blank=True)
	department = models.CharField(max_length=30, blank=True)
	group = models.CharField(max_length=30, blank=True)
	title = models.CharField(max_length=20, blank=True)
	avatar = models.ImageField(upload_to='avatars/', blank=True)

	def __unicode__(self):
		return self.user.username

	def __str__(self):
		return self.__unicode__()

	@staticmethod
	def get_developer(user):
		return Developer.objects.filter(user=user)


# Data model of project repository.
class Repo(models.Model):	
	owner = models.ForeignKey(Developer, related_name='owner', on_delete=models.CASCADE)
	members = models.ManyToManyField(Developer, related_name='members', blank=True)
	files = models.FileField(upload_to='sourcecode', blank=True)
	project_name = models.CharField(max_length=128, blank=False)
	create_time = models.DateTimeField(auto_now_add=True)
	modified_time = models.DateTimeField(auto_now=True)
	modify_frequency = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])	

	def __unicode__(self):
		return self.project_name

	def __str__(self):
		return self.__unicode__()



