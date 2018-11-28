from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from datetime import datetime, timezone

# User login and registration model
class Developer(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, primary_key=True)
    company = models.CharField(max_length=30, blank=True, default="Google")
    department = models.CharField(max_length=30, blank=True, default="IT")
    group = models.CharField(max_length=30, blank=True, default="1")
    title = models.CharField(max_length=20, blank=True, default="SDE")
    avatar = models.ImageField(upload_to='avatars/', blank=True, default='avatars/default-user-avatar.jpg')

    def __str__(self):
        return self.user.username

    @staticmethod
    def get_developer(user):
        return Developer.objects.filter(user=user)


class Reply(models.Model):
    replier = models.ForeignKey(Developer, on_delete=models.CASCADE)
    content = models.CharField(max_length=128)
    reply_time = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.id

    @property
    def html(self):
        res = "<hr><div class='left user-avatar' style='float:left;'> \
        <a href='profile/%s'> \
        <img src='%s' alt='Avatar of %s' style='float:left;width:50px;' />\
        </a>\
        </div>\
        <div class='divider'></div>\
        <div class='right' >\
        <p><a href='profile/%s'>  %s</a> replies on %s:</p>\
        <div class='divider'></div>\
        <h6>  %s</h6><hr>" % (self.replier, self.replier.avatar.url, self.replier, self.replier, self.replier,
                              self.reply_time.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime(
                                  '%Y-%m-%d %H:%M:%S'), self.content)
        return res


class Comment(models.Model):
    line_num = models.IntegerField()
    commenter = models.ForeignKey(Developer, related_name='commenter', on_delete=models.CASCADE)
    content = models.CharField(max_length=128)
    comment_time = models.DateTimeField(auto_now_add=True)
    reply = models.ManyToManyField(Reply, related_name='reply', blank=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.id

    @property
    def html(self):
        res = "<div class='left user-avatar' style='float:left;'> \
        <a href='profile/%s'> \
        <img src='%s' alt='Avatar of %s' style='float:left;width:75px;' />\
        </a>\
        </div>\
        <div class='divider'></div>\
        <div class='right' >\
        <p><a href='profile/%s'>  %s</a> on %s:</p>\
        <div class='divider'></div>\
        <h6>  %s</h6>" % (self.commenter, self.commenter.avatar.url, self.commenter, self.commenter, self.commenter,
                          self.comment_time.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime(
                              '%Y-%m-%d %H:%M:%S'), self.content)
        return res

    # res=res+"<table><tbody><tr><th><label for='id_commentcontent'>Comments... </label></th><td><input type='text' name='commentcontent' required id='id_commentcontent_%s'></td>\
    # <input type='hidden' name='post_id' value='%s' </tr>\
    # </tbody></table><div id='cmt-msg-%s' class='col-sm-offset-11'><button id='%s' type='submit' class='btn btn-success cmt-btn'>Send</button></div>\
    # <div id='cmt-list-%s'></div><hr>"% (self.id,self.id,self.id,self.id,self.id)

    # return self.commenter.user.username +' comments on '+(str(self.comment_time))+': '+self.content

    @staticmethod
    def get_comments(file_id, line_num):
        file_cmt = File.objects.get(id=file_id).comments.all()
        return Comment.objects.filter(id__in=file_cmt, line_num=line_num)

    @staticmethod
    def get_replies(comment):
        replies = comment.reply
        return Reply.objects.filter(id__in=replies)
# @staticmethod
# def get_reply_num(comment):
# 	return len(Comment.get_replies(comment))


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


class File(models.Model):
    file_name = models.FileField(upload_to='sourcecode', blank=True)
    repo = models.ForeignKey(Repo, on_delete=models.CASCADE, related_name="repository")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    comments = models.ManyToManyField(Comment, blank=True)
    from_github = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return 'file: {0}, {1}'.format(self.file_name.name, self.file_name.url)


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

class NewReplyMessage(models.Model):
    replier = models.ForeignKey(Developer, on_delete=models.CASCADE, related_name='new_reply_replier')
    new_reply_receiver = models.ForeignKey(Developer, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    @property
    def reply_message_body(self):
        content = self.comment.content
        if len(content)>6:
            content = content[:6]+"..."
        filename = self.file.file_name.name[11:]
        if len(filename)>15:
            filename = filename[:15]+"..."
        replier_name = self.replier.user.username
        return 'Your comment "{0}" at file "{1}" received a new reply from {2}.'.format(content,filename,replier_name)
