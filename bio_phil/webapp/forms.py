from django import forms
from .models import User, AccessCode, NewEmail, Submission
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm, PasswordResetForm
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

class CustomPasswordResetForm(PasswordResetForm):
	def __init__(self, *args, **kwargs):
		super(CustomPasswordResetForm, self).__init__(*args, **kwargs)
		self.fields['email'].widget.attrs={
			'id' : 'username',
			'class' : 'form-control',
		}

class LoginForm(AuthenticationForm):
	def __init__(self, *args, **kwargs):
		super(LoginForm, self).__init__(*args, **kwargs)
		self.fields['username'].widget.attrs={
			'id' : 'signInEmail',
			'class' : 'form-control',
		}
		self.fields['password'].widget.attrs={
			'id' : 'signinPassword',
			'class' : 'form-control',
		}

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

	def __init__(self, *args, **kwargs):
		super(RegisterForm, self).__init__(*args, **kwargs)
		self.fields['email'].widget.attrs={
			'id' : 'exampleInputEmail1',
			'class' : 'form-control',
			'aria-describedby' : 'emailHelp'
		}
		self.fields['first_name'].widget.attrs={
			'id' : 'exampleInputName',
			'class' : 'form-control',
			'aria-describedby' : 'emailHelp'
		}
		self.fields['last_name'].widget.attrs={
			'id' : 'exampleInputName',
			'class' : 'form-control',
			'aria-describedby' : 'emailHelp'
		}
		self.fields['password1'].widget.attrs={
			'id' : 'exampleInputPassword1',
			'class' : 'form-control',
		}
		self.fields['password2'].widget.attrs={
			'id' : 'exampleInputPassword2',
			'class' : 'form-control',
		}
		self.fields['access_field'].widget.attrs={
			'id' : 'exampleInputAccess',
			'class' : 'form-control',
		}

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

	def __init__(self, *args, **kwargs):
		super(GenerateCodeForm, self).__init__(*args, **kwargs)
		self.fields['quantity'].widget.attrs={
			'id' : 'quantity',
			'class' : 'form-control',
			'placeholder' : 0
		}
		self.fields['user_type'].widget.attrs={
			'id' : 'userType',
			'class' : 'custom-select',
		}

class ChangePasswordForm(PasswordChangeForm):
	def __init__(self, *args, **kwargs):
		super(ChangePasswordForm, self).__init__(*args, **kwargs)
		self.fields['old_password'].widget.attrs={
			'id' : 'currentPassword',
			'class' : 'form-control'
		}
		self.fields['new_password1'].widget.attrs={
			'id' : 'newPassword',
			'class' : 'form-control'
		}
		self.fields['new_password2'].widget.attrs={
			'id' : 'newPassword2',
			'class' : 'form-control'
		}

class ChangeEmailForm(forms.ModelForm):
	confirm_email = forms.EmailField()
	old_email = forms.EmailField(disabled=True)

	class Meta:
		model = NewEmail
		fields = ['old_email', 'new_email', 'confirm_email']

	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop("request")
		super(ChangeEmailForm, self).__init__(*args, **kwargs)
		self.fields['old_email'].initial = self.request.user.email

		self.fields['old_email'].widget.attrs={
			'id' : 'currentEmail',
			'class' : 'form-control',
		}
		self.fields['new_email'].widget.attrs={
			'id' : 'newEmail',
			'class' : 'form-control'
		}
		self.fields['confirm_email'].widget.attrs={
			'id' : 'newEmail2',
			'class' : 'form-control'
		}

	def is_valid(self):
        # run the parent validation first
		valid = super(ChangeEmailForm, self).is_valid()
 
        # we're done now if not valid
		if not valid:
			return valid
 
		new_email = self.cleaned_data['new_email']
		confirm_email = self.cleaned_data['confirm_email']
		old_email = self.cleaned_data['old_email']

		if new_email != confirm_email:
			self.add_error('confirm_email', "Emails do not match.")
			return False

		if User.objects.filter(email=new_email).count() > 0:
			self.add_error('new_email', "Email is already taken.")
			return False

		return True

class SubmitForm(forms.ModelForm):
	class Meta:
		model = Submission
		fields = ['file']

	def __init__(self, *args, **kwargs):
		super(SubmitForm, self).__init__(*args, **kwargs)
		self.fields['file'].widget.attrs={
			'id' : 'inputGroupFile',
			'class' : 'custom-file-input'
		}

class AdminAccessCodeAddForm(forms.ModelForm):
	quantity = forms.IntegerField()

	class Meta:
		model = AccessCode
		fields = ['quantity', 'user_type', 'university']

class AdminAccessCodeChangeForm(forms.ModelForm):
	class Meta:
		model = AccessCode
		fields = ['access_code', 'user_type', 'university']
