from django import forms
from .models import User, AccessCode
from django.contrib.auth.forms import UserCreationForm

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
		fields = ['quantity']


class AdminAccessCodeAddForm(forms.ModelForm):
	quantity = forms.IntegerField()

	class Meta:
		model = AccessCode
		fields = ['quantity', 'user_type', 'university']

class AdminAccessCodeChangeForm(forms.ModelForm):
	class Meta:
		model = AccessCode
		fields = ['access_code', 'user_type', 'university']
