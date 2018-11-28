from django.test import TestCase
from codereviewer.models import *
from django.contrib.auth.models import User


# test Developer model
class DeveloperTestCase(TestCase):
    def setUp(self):
        u1 = User.objects.create_user(username='u1', first_name='user1', last_name='l1', password='pw1')
        d1 = Developer.objects.create(user=u1)
        u2 = User.objects.create_user(username='u2', first_name='user2', last_name='l2', password='pw2')
        d2 = Developer.objects.create(user=u2, company='Google')
        u3 = User.objects.create_user(username='u3', first_name='user3', last_name='l3', password='pw3',
                                      email='user3@gmail.com')
        d3 = Developer.objects.create(user=u3)

    def test_user_creation(self):
        u1 = User.objects.get(first_name='user1')
        u2 = User.objects.get(last_name='l2')
        self.assertEqual(u1.first_name, 'user1')
        self.assertEqual(u2.last_name, 'l2')

    def test_company(self):
        u2 = User.objects.get(last_name='l2')
        d2 = Developer.objects.get(user=u2)
        self.assertEqual(d2.company, 'Google')

    def test_email(self):
        u3 = User.objects.get(username='u3')
        d3 = Developer.objects.get(user=u3)
        self.assertEqual(u3.email, 'user3@gmail.com')


# test Reply model
class ReplyTestCase(TestCase):
    def setUp(self):
        u1 = User.objects.create_user(username='u1', first_name='user1', last_name='l1', password='pw1')
        d1 = Developer.objects.create(user=u1)
        u2 = User.objects.create_user(username='u2', first_name='user2', last_name='l2', password='pw2')
        d2 = Developer.objects.create(user=u2, company='Google')

        Reply.objects.create(replier=d1, content='reply 1')
        Reply.objects.create(replier=d2, content='reply 2', deleted=True)

    def test_reply_creation(self):
        u1 = User.objects.get(username='u1')
        d1 = Developer.objects.get(user=u1)
        r1 = Reply.objects.get(replier=d1)
        self.assertEqual(r1.content, 'reply 1')

    def test_reply_delete(self):
        u2 = User.objects.get(username='u2')
        d2 = Developer.objects.get(user=u2)
        r2 = Reply.objects.get(replier=d2)
        self.assertTrue(r2.deleted)


# test Comment model
class CommentTestCase(TestCase):
    def setUp(self):
        u1 = User.objects.create_user(username='u1', first_name='user1', last_name='l1', password='pw1')
        d1 = Developer.objects.create(user=u1)

        c1 = Comment.objects.create(line_num=10, commenter=d1, content='comment 1')

    def test_comment_creation(self):
        u1 = User.objects.get(username='u1')
        d1 = Developer.objects.get(user=u1)
        c1 = Comment.objects.get(commenter=d1)
        self.assertEqual(c1.content, 'comment 1')


# test Repo model
class RepoTestCase(TestCase):
    def setUp(self):
        u1 = User.objects.create_user(username='u1', first_name='user1', last_name='l1', password='pw1')
        d1 = Developer.objects.create(user=u1)
        u2 = User.objects.create_user(username='u2', first_name='user2', last_name='l2', password='pw2')
        d2 = Developer.objects.create(user=u2, company='Google')
        u3 = User.objects.create_user(username='u3', first_name='user3', last_name='l3', password='pw3',
                                      email='user3@gmail.com')
        d3 = Developer.objects.create(user=u3)

        p1 = Repo.objects.create(owner=d1, project_name='project1')
        p2 = Repo.objects.create(owner=d2, project_name='project2')
        p2.members.add(d3)

    def test_repo_creation(self):
        u1 = User.objects.get(username='u1')
        d1 = Developer.objects.get(user=u1)
        p1 = Repo.objects.get(owner=d1)
        self.assertEqual(p1.project_name, 'project1')

    def test_add_member(self):
        u2 = User.objects.get(username='u2')
        d2 = Developer.objects.get(user=u2)
        u3 = User.objects.get(username='u3')
        d3 = Developer.objects.get(user=u3)
        p2 = Repo.objects.get(owner=d2)
        self.assertIn(d3, p2.members.all())


# test invitation model
class InvitationTestCase(TestCase):
    def setUp(self):
        u1 = User.objects.create_user(username='u1', first_name='user1', last_name='l1', password='pw1')
        d1 = Developer.objects.create(user=u1)
        u2 = User.objects.create_user(username='u2', first_name='user2', last_name='l2', password='pw2')
        d2 = Developer.objects.create(user=u2, company='Google')
        p1 = Repo.objects.create(owner=d1, project_name='project1')

        InvitationMessage.objects.create(sender=d1, receiver=d2, project=p1)

    def test_msg_creation(self):
        u1 = User.objects.get(username='u1')
        d1 = Developer.objects.get(user=u1)
        u2 = User.objects.get(username='u2')
        d2 = Developer.objects.get(user=u2)
        r1 = Repo.objects.get(project_name='project1')
        m1 = InvitationMessage.objects.get(sender=d1, receiver=d2)
        self.assertEqual(m1.project, r1)
