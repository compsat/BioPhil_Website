from django import forms
from .models import User, AccessCode, NewEmail
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.contrib.auth import authenticate

class ResendForm(forms.Form):
	email = forms.EmailField()

	def is_valid(self):
		valid = super(ResendForm, self).is_valid()

		if not valid:
			return valid

		email = self.cleaned_data['email']

		if User.objects.filter(email=email).count() == 0:
			self.add_error('email', "This email does not exist as a user.")
			return False
		else:
			user = User.objects.get(email=email)
			if user.is_active:
				self.add_error('email', "This email is already verified.")
				return False

		return True

class LoginForm(AuthenticationForm):
	def is_valid(self):
 
        # run the parent validation first
		valid = super(AuthenticationForm, self).is_valid()

		email = self.cleaned_data['username']
		password = self.cleaned_data['password']

		if User.objects.filter(email=email).count() == 0:
			return False
		else:
			user = User.objects.get(email=email)
			if not user.is_active:
				self.add_error('username', "You have not verified your email")
				return False

        # we're done now if not valid
		if not valid:
			return valid

		return True

class RegisterForm(UserCreationForm):
	access_field = forms.CharField(max_length=20)

	class Meta:
		model = User
		fields = ['email', 'first_name', 'last_name', 'access_field']

	def is_valid(self):
 
        # run the parent validation first
		valid = super(RegisterForm, self).is_valid()
 
        # we're done now if not valid
		if not valid:
			return valid

		access_code = self.cleaned_data['access_field']
 
		try:
			access_object = AccessCode.objects.get(access_code=access_code)
 
		except AccessCode.DoesNotExist:
			self.add_error('access_field', "Invalid access code")
			return False

		if hasattr(AccessCode.objects.get(access_code=access_code), 'user'):
			self.add_error('access_field', "Access code has been used")
			return False
 
		return True

class GenerateCodeForm(forms.ModelForm):
	quantity = forms.IntegerField()

	class Meta:
		model = AccessCode
		fields = ['quantity', 'user_type']

class ChangePasswordForm(PasswordChangeForm):
	pass 

class ChangeEmailForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput)
	confirm_email = forms.EmailField()

	class Meta:
		model = NewEmail
		fields = ['password', 'old_email', 'new_email', 'confirm_email']

	def is_valid(self):
        # run the parent validation first
		valid = super(ChangeEmailForm, self).is_valid()
 
        # we're done now if not valid
		if not valid:
			return valid
 
		password = self.cleaned_data['password']
		new_email = self.cleaned_data['new_email']
		confirm_email = self.cleaned_data['confirm_email']
		old_email = self.cleaned_data['old_email']

		if new_email != confirm_email:
			self.add_error('confirm_email', "Emails do not match.")
			return False

		if User.objects.filter(email=new_email).count() > 0:
			self.add_error('new_email', "Email is already taken.")
			return False

		user = authenticate(email=old_email, password=password)

		if user is None:
			self.add_error('password', "Invalid password")
			return False

		return True

class AdminAccessCodeAddForm(forms.ModelForm):
	quantity = forms.IntegerField()

	class Meta:
		model = AccessCode
		fields = ['quantity', 'user_type', 'university']

class AdminAccessCodeChangeForm(forms.ModelForm):
	class Meta:
		model = AccessCode
		fields = ['access_code', 'user_type', 'university']
