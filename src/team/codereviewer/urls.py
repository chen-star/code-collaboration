from django.conf.urls import url
from django.urls import path, re_path

from codereviewer import views

urlpatterns = [
    url(r'^settings/?$', views.settings, name='settings'),
    url(r'^repositories/?$', views.repositories, name='repo'),
    url(r'create_repo', views.create_repo, name='create_repo'),
    url(r'edit_profile', views.edit_profile, name='edit_profile'),
    url(r'^review/(?P<file_id>.+)$', views.review, name='review'),
    url(r'^review_repo/(?P<repo_id>.+)$', views.review_repo, name='review_repo'),
    url(r'^mark_read_then_review/(?P<msg_id>.+)$', views.mark_read_then_review, name='mark_read_then_review'),
    url(r'^mark_read_then_review_new_reply/(?P<msg_id>.+)$', views.mark_read_then_review_new_reply, name='mark_read_then_review_new_reply'),
    url(r'^get-comments/(?P<file_id>.+)/(?P<line_num>.+)$', views.get_comments),
    url(r'^get-codes/(?P<file_id>.+)$', views.get_codes),
    url(r'^add-comment', views.add_comment),
    url(r'^delete-comment', views.delete_comment),
    url(r'^get-changes/(?P<file_id>.+)/(?P<line_num>.+)/(?P<time>.+)$', views.get_changed_comments),
    url(r'^add-reply', views.add_reply),
    url(r'^send-new-reply-msg', views.send_new_reply_msg),
    url(r'^registration/?$', views.registration, name='registration'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'^home$', views.index, name='home'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('invite', views.invite, name='invite'),
    re_path('resetpwd', views.resetpassword, name='resetpassword'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            views.confirmpassword, name='password_confirm'),
    path('reset/', views.confirmpassword_helper, name='resetp'),
    url(r'github_login/$', views.github_login, name='github_login'),
    url(r'github/$', views.github_auth, name='github_oauth'),
    url(r'githubRepo/$', views.get_repo_from_github, name='github_repo'),
    url(r'^search', views.search_bar, name='search'),
]
