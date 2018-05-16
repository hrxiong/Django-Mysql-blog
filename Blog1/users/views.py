from django.shortcuts import render

from django.http import HttpResponseRedirect
from django.urls import reverse

from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import UsersUserinfo, AuthUser
# Create your views here.

def logout_view(request):
	logout(request)
	return HttpResponseRedirect(reverse('users:login'))

def register(request):
	"""sign in as a new user"""
	if request.method != 'POST':
		form = UserCreationForm()
	else:
		form = UserCreationForm(data=request.POST)
		
		if form.is_valid():
			#save new user
			new_user = form.save()
			tempUser = AuthUser.objects.get(username=new_user.username)
			user_profile = UsersUserinfo(user=tempUser, photo='photos/user1.jpg')
			user_profile.save()
			
			#login
			authenticated_user = authenticate(username=new_user.username,password=request.POST['password1'])
			login(request,authenticated_user)
			
			#goto blog mainpage
			return HttpResponseRedirect(reverse('blog:mainpage'))
	context ={'form': form}
	return render(request, 'users/register.html', context)
