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


# test Reply mode
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