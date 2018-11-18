from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User


# User login and registration model
class Developer(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, primary_key=True)
    company = models.CharField(max_length=30, blank=True, default="Google")
    department = models.CharField(max_length=30, blank=True, default="IT")
    group = models.CharField(max_length=30, blank=True, default="1")
    title = models.CharField(max_length=20, blank=True, default="SDE")
    avatar = models.ImageField(upload_to='avatars/', blank=True)

    def __str__(self):
        return self.user.username

    @staticmethod
    def get_developer(user):
        return Developer.objects.filter(user=user)


# Data model of project repository.
class Repo(models.Model):
    owner = models.ForeignKey(Developer, related_name='owner', on_delete=models.CASCADE)
    members = models.ManyToManyField(Developer, related_name='members', blank=True)
    project_name = models.CharField(max_length=128, blank=False)
    create_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    modify_frequency = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])

    def __unicode__(self):
        return "project_name=" + self.project_name + " owner=" + self.owner.user.username + " create_time=" + str(
            self.create_time)

    def __str__(self):
        return self.__unicode__()

    @staticmethod
    def get_membering_repos(user):
        member = Developer.get_developer(user)
        return Repo.objects.filter(members__in=member)

    @staticmethod
    def get_owning_repos(user):
        owner = Developer.get_developer(user)
        return Repo.objects.filter(owner__in=owner)

    # def __str__(self):
    # 	return self.commenter.user.username +' comments on '+(str(self.comment_time))+': '+self.content

    @property
    def html(self):
        return __str__

    # def __str__(self):
    # 	return self.commenter.user.username +' comments on '+(str(self.comment_time))+': '+self.content

    @property
    def html(self):
        return __str__(self)


class File(models.Model):
    file_name = models.FileField(upload_to='sourcecode', blank=True)
    repo = models.ForeignKey(Repo, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'file: {0}'.format(self.file.file)


# User Invitation Message
class InvitationMessage(models.Model):
    sender = models.ForeignKey(Developer, on_delete=models.CASCADE, related_name='sender_msg')
    receiver = models.ForeignKey(Developer, on_delete=models.CASCADE, related_name='receiver_msg')
    project = models.ForeignKey(Repo, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    @staticmethod
    def get_membering_repos(user):
        member = Developer.get_developer(user)
        return Repo.objects.filter(members__in=[member])

    @staticmethod
    def get_files(user):
        return Repo.objects.all()

    def __str__(self):
        return 'sender: {0}, receiver: {1}'.format(self.sender, self.receiver)


class Comment(models.Model):
    file = models.ForeignKey(File, related_name='file', on_delete=models.CASCADE)
    line_num = models.IntegerField()
    commenter = models.ForeignKey(Developer, related_name='commenter', on_delete=models.CASCADE)
    content = models.CharField(max_length=128)
    comment_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.commenter.user.username + ' comments on ' + (str(self.comment_time)) + ': ' + self.content

    @property
    def html(self):
        return __str__(self)
