"""define urlpatterns of users"""
from django.conf.urls import url

from . import views

app_name = 'blog_urls'

urlpatterns = [
	#hello page
	url(r'^$', views.index, name='index'),
	#mainpage
	url(r'^mainpage/$', views.mainpage, name='mainpage'),
	
	
	#博客部分url
	#blogs
	url(r'^blogs/$', views.blogs, name='blogs'),
	url(r'^blogs/my_blog/$', views.my_blog, name='my_blog'),
	url(r'^blogs/new_blog/$', views.new_blog, name='new_blog'),
	url(r'^blogs/edit_blog/(?P<blog_id>\d+)/$', views.edit_blog, name='edit_blog'),
	url(r'^blogs/delete_blog/(?P<blog_id>\d+)/$', views.delete_blog, name='delete_blog'),


	#微博评论
	url(r'^blogs/comment_blog/(?P<blog_id>\d+)/$', views.comment_blog, name='comment_blog'),
	url(r'^blogs/edit_comment/(?P<comment_id>\d+)/$', views.edit_comment, name='edit_comment'),
	url(r'^blogs/delete_comment/(?P<comment_id>\d+)/$', views.delete_comment, name='delete_comment'),

	
	#好友部分url
	#需要添加查看好友信息以及删除好友操作
	
	#friends
	url(r'^friends/$', views.friends, name='friends'),
	url(r'^friends/add_friends$', views.add_friends, name='add_friends'),
	url(r'^friends/friends_info/(?P<f_username>\w+)/$', views.friends_info, name='friends_info'),
	url(r'^friends/add_friends/add_by_username/(?P<add_username>\w+)/$', views.add_by_username, name='add_by_username'),
	
	
	#消息部分url
	#messages
	url(r'^messages/$', views.messages, name='messages'),
	url(r'^messages/message_op/(?P<checkid>\d+)/(?P<op>\d+)/$', views.message_op, name='message_op'),
	
	
	
	#账户部分url
	#account
	url(r'^account/$', views.account, name='account'),
	#edit photo
	url(r'^account/edit_photo$', views.edit_photo, name='edit_photo'),
	#edit account
	url(r'^account/edit_account$', views.edit_account, name='edit_account'),
	#edit password
	url(r'^account/edit_password$', views.edit_password, name='edit_password'),
]
