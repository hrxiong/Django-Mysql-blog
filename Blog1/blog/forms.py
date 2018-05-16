from django import forms
import re

def email_check(email):
	pattern = re.compile(r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?")
	return re.match(pattern, email)

class UserinfoForm(forms.Form):
	first_name = forms.CharField(label='First Name', max_length=50, required=False)
	last_name = forms.CharField(label='Last Name', max_length=50, required=False)
	nickname = forms.CharField(label='Nickname', max_length=20, required=False)
	sex = forms.ChoiceField(label='gender', choices=(('Male','Male'),('Female','Female'), ('','')), required=False)
	birthday = forms.DateField(label='birthday', required=False)
	email = forms.EmailField(label='Email', required=False)
	address = forms.CharField(label='address', max_length=45, required=False)
	motto = forms.CharField(label='motto', max_length=145, required=False)
	
	def clean_first_name(self):
		c_first_name = self.cleaned_data.get('first_name')
		if len(c_first_name) >50:
			raise forms.ValidationError("Your first name is too long.")
		return c_first_name

	def clean_last_name(self):
		c_last_name = self.cleaned_data.get('last_name')
		if len(c_last_name) > 50:
			raise forms.ValidationError("Your last name is too long.")
		return c_last_name

	def clean_nickname(self):
		c_nickname = self.cleaned_data.get('nickname')
		if len(c_nickname) > 20:
			raise forms.ValidationError("Your nickname is too long.")
		return c_nickname
		
	def clean_email(self):
		c_email = self.cleaned_data.get('email')
		return c_email

	def clean_address(self):
		c_address = self.cleaned_data.get('address')
		if len(c_address) > 45:
			raise forms.ValidationError("Your address is too long.")
		return c_address
		
	def clean_motto(self):
		c_motto = self.cleaned_data.get('motto')
		if len(c_motto) > 145:
			raise forms.ValidationError("Your motto is too long.")
		return c_motto



class PwdChangeForm(forms.Form):
	old_password = forms.CharField(label='Old password', widget=forms.PasswordInput)
	
	password1 = forms.CharField(label='New Password', widget=forms.PasswordInput)
	password2 = forms.CharField(label='Password Confirmation', widget=forms.PasswordInput)
	
	# Use clean methods to define custom validation rules
	
	def clean_password1(self):
		password1 = self.cleaned_data.get('password1')
		
		if len(password1) < 6:
			raise forms.ValidationError("Your password is too short.")
		elif len(password1) > 20:
			raise forms.ValidationError("Your password is too long.")
		return password1
	
	def clean_password2(self):
		password1 = self.cleaned_data.get('password1')
		password2 = self.cleaned_data.get('password2')
		
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Password mismatch. Please enter again.")
		return password2
		
class AddFriendForm(forms.Form):
	text = forms.CharField(label='Search Account', max_length=50)
	choose_type = forms.ChoiceField(label='type', choices=(('Username','Username'),('Nickname','Nickname')))

class SearchFriendForm(forms.Form):
	text = forms.CharField(label='Search Friend', max_length=50, required=False)
	choose_type = forms.ChoiceField(label='type', choices=(('Username','Username'),('Nickname','Nickname')))

class BlogForm(forms.Form):
	text = forms.CharField(label='blog', max_length=200, required=False)


class CommentForm(forms.Form):
	text = forms.CharField(label='Comment', max_length=200)
