from django.shortcuts import render
from users.models import UsersUserinfo, Friends, CheckFriends
from django.contrib.auth.models import User
from .forms import UserinfoForm, PwdChangeForm, AddFriendForm, SearchFriendForm, BlogForm, CommentForm
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.urls import reverse
from .models import BlogsBlog, BlogPhoto, BlogComments
from django.db import connection
from django.forms.models import model_to_dict

import os
import time, datetime
import json
from operator import itemgetter
from PIL import Image
# Create your views here.

class Mem:
	cur = {}

def get_info_with_id(to_get_id):
	user = User.objects.get(id=to_get_id)
	user_info = UsersUserinfo.objects.get(user_id=to_get_id)
	ret = {'userinfo': user_info, 'user':user }
	return ret


def index(request):
	return render(request, 'blog/index.html')

@login_required
def mainpage(request):
	context = {'account': UsersUserinfo.objects.get(user_id=request.user.id), 'user': request.user}
	return render(request, 'blog/mainpage.html', context)
	

class CJsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, datetime.datetime):
			return obj.strftime('%Y-%m-%d %H:%M:%S')
		elif isinstance(obj, datetime.date):
			return obj.strftime('%Y-%m-%d')
		else:
			return json.JSONEncoder.default(self, obj)

def refactoringBlog(obj):
	temp = {}
	#blog info
	temp['id'] = obj[0]
	temp['senduser'] = model_to_dict(UsersUserinfo.objects.get(id=obj[1]))
	#temp['username'] = User.objects.get(id=temp['senduser'].user_id).username
	temp['user'] = model_to_dict(User.objects.get(id=temp['senduser']['user']))
	temp['content'] = obj[2]
	temp['time'] = obj[3]
	photo = []
	tempphotos = BlogPhoto.objects.filter(blog_id=obj[0])
	for p in tempphotos:
		photo.append(model_to_dict(p))
	temp['photo'] = photo
	
	#comments info
	blog = BlogsBlog.objects.get(id=obj[0])
	comments = blog.blogcomments_set.all()
	coms = []
	for comment in comments:
		com = {}
		com['comment_userinfo'] = model_to_dict(UsersUserinfo.objects.get(id=comment.creator_id))
		#com['comment_username'] = User.objects.get(id=com['comment_userinfo'].user_id).username
		com['comment_user'] = model_to_dict(User.objects.get(id=com['comment_userinfo']['user']))
		com['comment'] = model_to_dict(comment)
		com['time'] = comment.createtime
		coms.append(com)
	coms = sorted(coms, key=itemgetter('time'))
	temp['comments'] = coms
	
	return temp

@login_required
def blogs(request):
	user_info = UsersUserinfo.objects.get(user_id=request.user.id)
	user = request.user
	if request.method == "POST":
		mem = Mem()
		blog_list = []
		for i in range(0,10):
			blog = mem.cur[user.username].fetchone()
			if blog:
				blog_list.append(refactoringBlog(blog))
			else:
				break;
		data = json.dumps({'acc':model_to_dict(user_info), 'blog_list': blog_list}, cls=CJsonEncoder)
		return HttpResponse(data)
	Mem.cur[user.username] = connection.cursor()
	mem = Mem()
	mem.cur[user.username].execute(""" select * 
					from blogs_blog 
					where users_userinfo_id = %s 
						  or 
						  users_userinfo_id in 
						  (select X.user1 from friends as X where X.user2 = %s)
						  or 
						  users_userinfo_id in 
						  (select Y.user2 from friends as Y where Y.user1 = %s) 
					order by createtime desc;""",[str(user_info.id),str(user_info.id),str(user_info.id)])
	blog_list = []
	for i in range(0,10):
		blog = mem.cur[user.username].fetchone()
		if blog:
			blog_list.append(refactoringBlog(blog))
		else:
			break;
	
	
	# ~ , 'cursor': json.dumps({'cursor':cur})
	context = {'account': user_info, 'blog_list': json.dumps(blog_list, cls=CJsonEncoder),
			'user': user, 'acc':json.dumps(model_to_dict(user_info), cls=CJsonEncoder)}
	return render(request, 'blog/blogs.html', context)
	
@login_required
def my_blog(request):
	user_info = UsersUserinfo.objects.get(user_id=request.user.id)
	cur = connection.cursor()
	cur.execute(""" select * 
					from blogs_blog 
					where users_userinfo_id = %s 
					order by createtime desc;""",[str(user_info.id)])
	blogs = cur.fetchall()
	blog_list = []
	for blog in blogs:
		blog_list.append(refactoringBlog(blog))

	context = {'account': user_info, 'blogs': blog_list, 'user': request.user, 'acc': user_info}
	return render(request, 'blog/blogs.html', context)

@login_required
def new_blog(request):
	user_info = UsersUserinfo.objects.get(user_id=request.user.id)
	if request.method == 'POST':
		form = BlogForm(request.POST)
		if form.is_valid():
			get_text = form.cleaned_data['text']
			new_blog = BlogsBlog(text=get_text, users_userinfo_id=user_info.id)
			new_blog.save()
			
			photos = request.FILES.getlist('photos')
			if photos:
				cnt = 0
				for photo in photos:
					cnt = cnt + 1
					phototime = str(time.time()).split('.')[0]
					photo_last = str(photo).split('.')[-1]
					photoname = request.user.username + '/photos/' + str(cnt) + '_%s.%s'%(phototime,photo_last)
					img = Image.open(photo)

					#new user
					SavePath = 'blog/static/' + request.user.username + '/photos'
					SavePath = SavePath.strip()
					isExist = os.path.exists(SavePath)
					if not isExist:
						os.makedirs(SavePath)
					
					'''#delete old picture
					old_path = 'users/static/' + (UsersUserinfo.objects.get(user_id=request.user.id)).photo
					if(os.path.exists(old_path)):
						os.remove(old_path)'''
					
					new_photo = BlogPhoto(blog_id=new_blog.id, photo=photoname)
					new_photo.save()
					img.save('blog/static/' + photoname)
	else:
		form = BlogForm()
	
	context = {'account': user_info, 'form': form, 'user': request.user}
	return render(request, 'blog/new_blog.html', context)
	
	
@login_required
def edit_blog(request,blog_id):
	user_info = UsersUserinfo.objects.get(user_id=request.user.id)
	blog_to_edit = BlogsBlog.objects.get(id=blog_id)
	if blog_to_edit.users_userinfo_id != user_info.id:
		raise Http404
	form = BlogForm({'text':blog_to_edit.text})
	if request.method == 'POST':
		form = BlogForm(request.POST)
		if form.is_valid():
			get_text = form.cleaned_data['text']
			BlogsBlog.objects.filter(id=blog_id).update(text=get_text,createtime= datetime.datetime.now())
			'''可以修改为加载原来的照片'''
			#删除原来的照片
			photos_to_delete = BlogPhoto.objects.filter(blog_id=blog_id)
			
			for item in photos_to_delete:
				#delete old picture
				old_path = 'blog/static/' + item.photo
				if(os.path.exists(old_path)):
					os.remove(old_path)
			photos_to_delete.delete()
			
			#删除原来的评论
			BlogComments.objects.filter(blog_id=blog_id).delete()
			
			photos = request.FILES.getlist('photos')
			if photos:
				cnt = 0
				for photo in photos:
					cnt = cnt + 1
					phototime = str(time.time()).split('.')[0]
					photo_last = str(photo).split('.')[-1]
					photoname = request.user.username + '/photos/' + str(cnt) + '_%s.%s'%(phototime,photo_last)
					img = Image.open(photo)

					#new user
					SavePath = 'blog/static/' + request.user.username + '/photos'
					SavePath = SavePath.strip()
					isExist = os.path.exists(SavePath)
					if not isExist:
						os.makedirs(SavePath)
					'''#delete old picture
					old_path = 'users/static/' + (UsersUserinfo.objects.get(user_id=request.user.id)).photo
					if(os.path.exists(old_path)):
						os.remove(old_path)'''
					new_photo = BlogPhoto(blog_id=blog_to_edit.id, photo=photoname)
					new_photo.save()
					img.save('blog/static/' + photoname)
	else:
		photos_to_delete = BlogPhoto.objects.filter(blog_id=blog_id)
			#用户取消更新时，图片不能消失，利用数据库的cascade特性进行删除
			#photos_to_delete.delete()
	context = {'account': user_info, 'form': form, 'user': request.user}
	return render(request, 'blog/new_blog.html', context)


@login_required
def delete_blog(request,blog_id):
	user_info = UsersUserinfo.objects.get(user_id=request.user.id)
	blog = BlogsBlog.objects.get(id=blog_id)
	if blog.users_userinfo_id != user_info.id:
		raise Http404
		
	#删除图片和微博
	photos_to_delete = BlogPhoto.objects.filter(blog_id=blog_id)
	for item in photos_to_delete:
		#delete old picture
		old_path = 'blog/static/' + item.photo
		if(os.path.exists(old_path)):
			os.remove(old_path)
	
	BlogsBlog.objects.filter(id=blog_id).delete()
	return HttpResponseRedirect(reverse('blog:blogs'))



'''
需要在博客页面添加评论按钮
传入博客相关评论以及评论者相关信息
并且显示评论的删除和编辑
删除操作可能需要添加逻辑（博客本人能够删除评论）
'''
@login_required
def comment_blog(request,blog_id):
	user_info = UsersUserinfo.objects.get(user_id=request.user.id)
	if request.method == 'POST':
		form = CommentForm(request.POST)
		if form.is_valid():
			get_text = form.cleaned_data['text']
			new_comment = BlogComments(text=get_text, creator_id=user_info.id, blog_id=blog_id)
			new_comment.save()
			return HttpResponseRedirect(reverse('blog:blogs'))
	else:
		form = CommentForm()
	
	context = {'account': user_info, 'form': form, 'blog_id': blog_id, 'user': request.user}
	return render(request, 'blog/new_comment.html', context)

@login_required
def edit_comment(request,comment_id):
	user_info = UsersUserinfo.objects.get(user_id=request.user.id)
	old_comment = BlogComments.objects.get(id=comment_id)

	if old_comment.creator_id != user_info.id:
		raise Http404
	old_text = old_comment.text
	form = CommentForm({'text': old_text})
	if request.method == 'POST':
		form = CommentForm(request.POST)
		if form.is_valid():
			get_text = form.cleaned_data['text']
			BlogComments.objects.filter(id=comment_id).update(text=get_text,createtime=datetime.datetime.now(),
														blog_id=old_comment.blog_id,creator_id=old_comment.creator_id)
			return HttpResponseRedirect(reverse('blog:blogs'))
	context = {'account': user_info, 'form': form, 'comment_id': comment_id, 'user': request.user}
	return render(request, 'blog/edit_comment.html', context)

@login_required
def delete_comment(request,comment_id):
	user_info = UsersUserinfo.objects.get(user_id=request.user.id)
	comment = BlogComments.objects.get(id=comment_id)
	comment_blog = BlogsBlog.objects.get(id=comment.blog_id)
	bloger = comment_blog.users_userinfo_id
	if comment.creator_id != user_info.id and bloger != user_info.id:
		raise Http404
	BlogComments.objects.filter(id=comment_id).delete()
	return HttpResponseRedirect(reverse('blog:blogs'))




def get_friends_info(user_info_id):
	info_list = []
	
	user_list1 = Friends.objects.filter(user1_id=user_info_id)
	for u in user_list1:
		info_temp = UsersUserinfo.objects.get(id=u.user2_id)
		user_temp = User.objects.get(id=info_temp.user_id)
		'''temp = {'photo': info_temp.photo, 'username': user_temp.username,
				'nickname': info_temp.nickname, 'motto': info_temp.motto}'''
		temp = {'user': user_temp, 'userinfo': info_temp, 'for_sort': user_temp.username}
		info_list.append(temp)
		
	user_list2 = Friends.objects.filter(user2_id=user_info_id)
	for u in user_list2:
		info_temp = UsersUserinfo.objects.get(id=u.user1_id)
		user_temp = User.objects.get(id=info_temp.user_id)
		'''temp = {'photo': info_temp.photo, 'username': user_temp.username,
				'nickname': info_temp.nickname, 'motto': info_temp.motto}'''
		temp = {'user': user_temp, 'userinfo': info_temp, 'for_sort': user_temp.username}
		info_list.append(temp)
	#info_list = sorted(info_list, key=itemgetter('username'))
	info_list = sorted(info_list, key=itemgetter('for_sort'))
	return info_list




@login_required
def friends(request):
	user = User.objects.get(id=request.user.id)
	user_info = UsersUserinfo.objects.get(user_id=request.user.id)
	#得到所有的好友信息
	info_list = get_friends_info(user_info.id)

	if request.method == "POST":
		form = SearchFriendForm(request.POST)
		if form.is_valid():
			choose_text = form.cleaned_data['text']
			choose_info_list = []
			if form.cleaned_data['choose_type'] == 'Username':
				if choose_text:
					for item in info_list:
						#if item['username'] == choose_text:
						if item['user'].username == choose_text:
							choose_info_list.append(item)
				else:
					choose_info_list = info_list
			else:
				if choose_text:
					for item in info_list:
						#if item['nickname'] == choose_text:
						if item['userinfo'].nickname == choose_text:
							choose_info_list.append(item)
				else:
					choose_info_list = info_list

			context = {'account': user_info, 'info_list': choose_info_list, 'form': form, 'user': request.user}
			return render(request, 'blog/friends.html', context)
	else:
		form = SearchFriendForm()
	context = {'account': user_info, 'info_list': info_list, 'form': form, 'user': request.user}
	return render(request, 'blog/friends.html', context)

@login_required
def friends_info(request,f_username):
	user_info = UsersUserinfo.objects.get(user_id=request.user.id)

	if request.method == "POST":
		friend = User.objects.get(username=f_username)
		friend_info = UsersUserinfo.objects.get(user_id=friend.id)
		
		Friends.objects.filter(user1_id=user_info.id, user2_id=friend_info.id).delete()
		Friends.objects.filter(user2_id=user_info.id, user1_id=friend_info.id).delete()
		
		CheckFriends.objects.filter(user1_ch_id=user_info.id, user2_ch_id=friend_info.id).delete()
		CheckFriends.objects.filter(user2_ch_id=user_info.id, user1_ch_id=friend_info.id).delete()
		'''需要修改'''
		return HttpResponseRedirect(reverse('blog:friends'))
	'''
	if request.method == "POST":
		temp = request.POST.get('username')
		de_user = User.objects.get(username=temp)
		de_user_info = UsersUserinfo.objects.get(user_id=de_user.id)
		
		#从friends表格中删除
		c1 = Friends.objects.filter(user1_id=de_user_info.id, user2_id=user_info.id).delete()
		c2 = Friends.objects.filter(user2_id=de_user_info.id, user1_id=user_info.id).delete()

		c3 = CheckFriends.objects.filter(user1_ch_id=user_info.id, user2_ch_id=friend_info.id).delete()
		c4 = CheckFriends.objects.filter(user2_ch_id=user_info.id, user1_ch_id=friend_info.id).delete()'''

	friend = User.objects.get(username=f_username)
	friend_info = UsersUserinfo.objects.get(user_id=friend.id)
	is_friends = 0
	c1 = Friends.objects.filter(user1_id=user_info.id, user2_id=friend_info.id)
	c2 = Friends.objects.filter(user2_id=user_info.id, user1_id=friend_info.id)
	if c1 or c2:
		is_friends = 1
		
	'''info = {'photo': friend_info.photo, 'username': friend.username,
			'nickname': friend_info.nickname, 'motto': friend_info.motto, 'is_friends': is_friends}'''
	info = {'user': friend, 'userinfo': friend_info, 'is_friends': is_friends}
	context = {'account': user_info, 'info': info, 'user': request.user}
	return render(request, 'blog/friends_info.html', context)

@login_required
def add_friends(request):
	if request.method == "POST":
		form = AddFriendForm(request.POST)
		if form.is_valid():
			info_list = []
			if form.cleaned_data['choose_type'] == 'Username':
				getlist = User.objects.filter(username = form.cleaned_data['text'])
				for item in getlist:
					info_list.append(get_info_with_id(item.id))
			else:
				getlist = UsersUserinfo.objects.filter(nickname = form.cleaned_data['text'])
				for item in getlist:
					info_list.append(get_info_with_id(item.user_id))
			context = {'account': UsersUserinfo.objects.get(user_id=request.user.id),
					'user': request.user, 'form': form, 'status': 1,'info_list': info_list}
			return render(request, 'blog/add_friends.html', context)
	else:
		form = AddFriendForm()
	context = {'account': UsersUserinfo.objects.get(user_id=request.user.id),
				'user': request.user, 'form': form, 'status': 0}
	return render(request, 'blog/add_friends.html', context)

@login_required
def add_by_username(request,add_username):
	add_user = User.objects.get(username=add_username)
	user=request.user
	
	add_user_info = UsersUserinfo.objects.get(user_id=add_user.id)
	user_info = UsersUserinfo.objects.get(user_id=user.id)
	
	context = {'account': user_info, 'user': request.user}
	
	c1 = Friends.objects.filter(user1_id=user_info.id, user2_id=add_user_info.id)
	c2 = Friends.objects.filter(user2_id=user_info.id, user1_id=add_user_info.id)
	c3 = CheckFriends.objects.filter(user1_ch_id=add_user_info.id, user2_ch_id=user_info.id)
	c4 = CheckFriends.objects.filter(user1_ch_id=user_info.id, user2_ch_id=add_user_info.id)
	
	if c1 or c2:  #已经为好友
		message="you have been friends."
		context['message'] = message
		return render(request, 'blog/add_by_username.html', context)
	elif c3:  #对方正在添加自己为好友
		c3.update(checked='Y')
		new_friend = Friends(user2_id=user_info.id, user1_id=add_user_info.id)
		new_friend.save()
		message="Add successfully."
		context['message'] = message
	elif c4:  #已经申请添加好友
		message="The add request had been sent. Please wait patiently."
		context['message'] = message
	else:  #添加好友
		new_check = CheckFriends(user1_ch_id=user_info.id, user2_ch_id=add_user_info.id, 
								checked='N')
		new_check.save()
		message="The add request have been sent. Please wait."
		context['message'] = message
	return render(request, 'blog/add_by_username.html', context)

	

def get_message_list(user_info_id):
	message = []
	#用户为申请者
	user_list1 = CheckFriends.objects.filter(user1_ch_id=user_info_id)
	for u in user_list1:
		info_temp = UsersUserinfo.objects.get(id=u.user2_ch_id)
		user_temp = User.objects.get(id=info_temp.user_id)
		# ~ temp = {'photo': info_temp.photo, 'username': user_temp.username,
				# ~ 'nickname': info_temp.nickname, 'motto': info_temp.motto,
				# ~ 'time': u.applicationtime, 'checkid': u.id}
		temp = {'user': user_temp,'userinfo': info_temp, 'for_sort': user_temp.username,
				'time': u.applicationtime, 'checkid': u.id}
		if u.checked == 'N':
			temp['status'] = 0 #需要等待
		elif u.checked == 'Y':
			temp['status'] = 1 #添加成功
		else:
			temp['status'] = 2 #被拒绝
		message.append(temp)
		
	#用户为被申请者
	user_list2 = CheckFriends.objects.filter(user2_ch_id=user_info_id)
	for u in user_list2:
		info_temp = UsersUserinfo.objects.get(id=u.user1_ch_id)
		user_temp = User.objects.get(id=info_temp.user_id)
		# ~ temp = {'photo': info_temp.photo, 'username': user_temp.username,
				# ~ 'nickname': info_temp.nickname, 'motto': info_temp.motto,
				# ~ 'time': u.applicationtime, 'checkid': u.id}
		temp = {'user': user_temp,'userinfo': info_temp, 'for_sort': user_temp.username,
				'time': u.applicationtime, 'checkid': u.id}
		if u.checked == 'N':
			temp['status'] = 3 #需要确认
		elif u.checked == 'Y':
			temp['status'] = 4 #添加成功
		else:
			temp['status'] = 5 #已拒绝
		message.append(temp)
	message = sorted(message, key=itemgetter('time','for_sort'), reverse=True)
	return message

@login_required
def messages(request):
	user_info = UsersUserinfo.objects.get(user_id=request.user.id)
	context = {'account': user_info, 'user': request.user}
	
	message = get_message_list(user_info.id)
	context['message'] = message
	
	return render(request, 'blog/messages.html', context)

def message_op(request, checkid, op):
	user_info = UsersUserinfo.objects.get(user_id=request.user.id)
	temp_checkitem = CheckFriends.objects.get(id=checkid)
	if temp_checkitem.user2_ch_id != user_info.id:
		raise Http404

	if op == '0':
		temp_checkitem = CheckFriends.objects.filter(id=checkid)
		temp_checkitem.update(checked='Y')
		temp_checkitem = CheckFriends.objects.get(id=checkid)
		new_friend = Friends(user1_id = temp_checkitem.user1_ch_id,
							user2_id = temp_checkitem.user2_ch_id)
		new_friend.save()
	elif op == '1':
		CheckFriends.objects.filter(id=checkid).update(checked='R')
	return HttpResponseRedirect(reverse('blog:messages'))

@login_required
def account(request):
	user = User.objects.get(id=request.user.id)
	user_info = UsersUserinfo.objects.get(user_id=request.user.id)
	# ~ info = {'nickname': user_info.nickname, 'motto': user_info.motto,
			# ~ 'first_name': user.first_name, 'last_name': user.last_name,
			# ~ 'sex': user_info.sex, 'birthday': user_info.birthday,
			# ~ 'address': user_info.address, 'email': user.email,}
	
	context = {'account': user_info, 'user': user}
	return render(request, 'blog/account.html', context)

@login_required
def edit_photo(request):
	user_info = UsersUserinfo.objects.get(user_id=request.user.id)
	if request.method=='POST':
		photo=request.FILES['image_file']
		if photo:
			x1=float(request.POST.get('x1'))
			y1=float(request.POST.get('y1'))
			x2=float(request.POST.get('x2'))
			y2=float(request.POST.get('y2'))
			divsize = float(request.POST.get('divw'))
			orisize = float(request.POST.get('filedim').split(' ')[0])
			resize = orisize/divsize
			
			phototime = str(time.time()).split('.')[0]
			photo_last = str(photo).split('.')[-1]
			photoname = request.user.username + '/photos/%s.%s'%(phototime,photo_last)
			img = Image.open(photo)
			
			#截取图片
			region = img.crop((x1*resize, y1*resize, x2*resize, y2*resize))

			#new user
			SavePath = 'users/static/' + request.user.username + '/photos'
			SavePath = SavePath.strip()
			isExist = os.path.exists(SavePath)
			if not isExist:
				os.makedirs(SavePath)
			
			old_path = 'users/static/' + (UsersUserinfo.objects.get(user_id=request.user.id)).photo
			if(os.path.exists(old_path)):
				os.remove(old_path)

			region.save('users/static/' + photoname)
			count = UsersUserinfo.objects.filter(user_id=request.user.id).update(photo=photoname)
			if count:
				return HttpResponseRedirect(reverse('blog:account'))
			else:#need add logic
				#return HttpResponse('上传失败')
				return HttpResponseRedirect(reverse('blog:account'))
		return HttpResponseRedirect(reverse('blog:account'))
		#return HttpResponse('图片为空')
	context = {'account': user_info, 'user': request.user}
	return render(request, 'blog/edit_photo.html', context)

@login_required
def edit_account(request):
	user = User.objects.get(id=request.user.id)
	user_info = UsersUserinfo.objects.get(user_id=request.user.id)
	if request.method == "POST":
		form = UserinfoForm(request.POST)

		if form.is_valid():
			user.first_name = form.cleaned_data['first_name']
			user.last_name = form.cleaned_data['last_name']
			user.email = form.cleaned_data['email']
			user.save()

			user_info.nickname = form.cleaned_data['nickname']
			user_info.birthday = form.cleaned_data['birthday']
			user_info.address = form.cleaned_data['address']
			user_info.motto = form.cleaned_data['motto']
			if form.cleaned_data['sex'] == 'Male':
				user_info.sex = 'Male'
			elif form.cleaned_data['sex'] == 'Female':
				user_info.sex = 'Female'
			else:
				user_info.sex = ''
			user_info.save()

			return HttpResponseRedirect(reverse('blog:account'))
	else:
		default_data = {'first_name': user.first_name, 'last_name': user.last_name,
						'email': user.email, 'nickname': user_info.nickname,
						'birthday': user_info.birthday, 'address': user_info.address,
						'motto': user_info.motto, 'sex': user_info.sex}
		form = UserinfoForm(default_data)
	context = {'account': user_info, 'form': form, 'user': request.user}
	return render(request, 'blog/edit_account.html', context)

@login_required
def edit_password(request):
	
	user = User.objects.get(id=request.user.id)
	if request.method == "POST":
		form = PwdChangeForm(request.POST)
		if form.is_valid():
			password = form.cleaned_data['old_password']
			username = user.username
			user = auth.authenticate(username=username, password=password)

			if user is not None and user.is_active:
				new_password = form.cleaned_data['password2']
				user.set_password(new_password)
				user.save()
				
				return HttpResponseRedirect(reverse('users:login'))
			else:
				return render(request, 'blog/edit_password.html', {'form': form,'user': user,
								'message': 'Old password is wrong. Try again'})
	else:
		form = PwdChangeForm()

	context = {'form': form, 'user': user,
				'account': UsersUserinfo.objects.get(user_id=request.user.id)}
	return render(request, 'blog/edit_password.html', context)


