#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import UserProfile,extendedUser
from django.contrib.auth import get_user_model

from django import forms
# from phonenumber_field.formfields import PhoneNumberField


from allauth.account.forms import LoginForm,SignupForm
from allauth.account.signals import email_confirmed
from django.db.models import F


from django.utils.translation import gettext, gettext_lazy as _

class Sign_upform(UserCreationForm):
	
	class Meta:

		model = User
		fields = ['username','first_name','last_name','email','password1','password2']
		
		widgets={
		'username':forms.TextInput(attrs={'placeholder':'UserName','class':'form-control'}),
		'first_name':forms.TextInput(attrs={'placeholder':'Fname','class':'form-control '}),
		'last_name':forms.TextInput(attrs={'placeholder':'Lname','class':'form-control '}),
		'email':forms.EmailInput(attrs={'placeholder':'Email','class':'form-control '}),
		# 'phone':forms.TextInput(attrs={'placeholder':'Phone','class':'form-control '}),
		# 'password1':forms.TextInput(attrs={'placeholder':'UserName','class':'form-control mt-4'}),
		}

	def __init__(self, *args, **kwargs):
		super(Sign_upform, self).__init__(*args, **kwargs)
		self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password from numbers and letters of the Latin alphabet'})
		self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password confirmation'})

	def clean_email(self):
		email = self.data.get("email")
		# email_chk = extendedUser.objects.filter(usr__email = email).count()
		# print(email_chk,"def")
		if extendedUser.objects.filter(usr__email = email).exists() :
			# print("inside")
			self.add_error(
                    "email",
                    _("Email Already in use"),)
			
		return email    
		
class myLoginForm(LoginForm):
	def __init__(self, *args, **kwargs):
		super(myLoginForm, self).__init__(*args, **kwargs)
		self.fields['login'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control','placeholder':'Username'})
		self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Password'})


class Registerform(forms.ModelForm):

	password1 = forms.CharField(label = "Password",widget=forms.PasswordInput(attrs = {'placeholder':'password','class':'form-control'}))
	password2 = forms.CharField(label = "Confirm Password",widget=forms.PasswordInput(attrs = {'placeholder':'Confirm password','class':'form-control'}))

	class Meta:

		model = User
		fields = ['username','first_name','last_name','email','password1','password2']
		
		widgets={
		'username':forms.TextInput(attrs={'placeholder':'UserName','class':'form-control'}),
		'first_name':forms.TextInput(attrs={'placeholder':'Fname','class':'form-control '}),
		'last_name':forms.TextInput(attrs={'placeholder':'Lname','class':'form-control '}),
		'email':forms.EmailInput(attrs={'placeholder':'Email','class':'form-control '}),
		}

class phoneUpdateform(forms.ModelForm):

	# password = forms.CharField(widget=forms.PasswordInput(attrs = {'placeholder':'password','class':'form-control mt-4'}))

	class Meta:

		model = extendedUser
		fields = ['phone']
		
		widgets = {'phone':forms.NumberInput(attrs={'placeholder':'Phone','class':'form-control',"minlength":'10'})	}


# clsss SignUpForm(forms.Form):
#     phone = forms.PhoneNumberField(label = "Password")
#     class Meta : 
#         model = User
#         fields = ['username','first_name','last_name','email','phone','password1','password2']

#     # password1 = forms.CharField(label = "Password",widget=forms.PasswordInput(attrs = {'placeholder':'password','class':'form-control'}))
	
#     def signup(self, req,user):


# class Registerform2(forms.ModelForm):

#     password1 = forms.CharField(label = "Password",widget=forms.PasswordInput(attrs = {'placeholder':'password','class':'form-control'}))
#     password2 = forms.CharField(label = "Confirm Password",widget=forms.PasswordInput(attrs = {'placeholder':'Confirm password','class':'form-control'}))
#     phone = forms.CharField(label = "Phone")
#     # class m
#     class Meta:

#         # model = User
#         model = get_user_model()
#         fields = ['username','first_name','last_name','email','phone','password1','password2']
		

#     def signup(self, request, user):
#             user.password1 = self.cleaned_data['password1']
#             user.password2 = self.cleaned_data['password2']
		 
#             print(user)
#             profile, created = models.extendedUser.objects.get_or_create(user=user)
#             up = user.profile
#             up.phone = self.cleaned_data['phone']
#             # up.organisation = self.cleaned_data['organisation']
#             user.save()
#             up.save()



# from allauth.account.forms import SignupForm
# from django import forms
 
 
# class CustomSignupForm(SignupForm):
#     first_name = forms.CharField(max_length=30, label='First Name')
#     last_name = forms.CharField(max_length=30, label='Last Name')
#     phone = forms.CharField(label = "Phone")

 
#     def signup(self, request, usr):
#         # def signup(self, user):
#         profile = extendedUser()
#         profile.save(commit = False)
#         usr.first_name = self.cleaned_data['first_name']
#         # usr.last_name = self.cleaned_data['last_name']
#         usr.save()
#         # usr.profile = profile
#         profile.user = usr     
#         profile.phone = self.cleaned_data['phone']
#         profile.save()
#         # usr.first_name = self.cleaned_data['first_name']
#         # usr.last_name = self.cleaned_data['last_name']
#         # profile, created = models.extendedUser.objects.get_or_create(user=usr)
#         # if created:
#         #     up = usr.created
#         # else:
#         #     up = usr.profile

#         # up.phone = self.cleaned_data['phone']
#         # usr.save()
#         # up.save()
#         # return usr
