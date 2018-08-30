from django.shortcuts import render, get_object_or_404, redirect
from .forms import RegisterForm, GenerateCodeForm
from .models import User, AccessCode, random_code_generator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def index(request):
	return render(request, 'webapp/index.html')

def register(request):
	if request.method == 'POST':
		form = RegisterForm(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			email = form.cleaned_data['email']
			password = form.cleaned_data['password1']
			access_code = form.cleaned_data['access_field']
			user.set_password(password)
			user.save()
			user = authenticate(email=email, password=password)
			if user is not None:
				if user.is_active:
					"""Attaches an access_object to the user based on the inputted access code"""
					access_object = AccessCode.objects.get(access_code=access_code)
					user.access_object = access_object
					user.save()
					login(request, user)
					return redirect('index')
	else:
		form = RegisterForm()
	return render(request, 'webapp/signup.html', {'form' : form})

"""View for teachers only for them to generate a specified number of access codes
either for their students or fellow teachers"""
@login_required
def generate_access_codes(request):
	if request.method == 'POST':
		teacher = request.user
		form = GenerateCodeForm(request.POST)
		if form.is_valid():
			access_object = form.save(commit=False)
			quantity = form.cleaned_data['quantity']
			user_type = form.cleaned_data['user_type']
			access_object.access_code = random_code_generator(5)
			access_object.user_type = user_type
			access_object.university = teacher.access_object.university
			access_object.creator = teacher
			access_object.save()
			for x in range(1, quantity):
				access_code = random_code_generator(5)
				obj = AccessCode.objects.create(access_code=access_code, user_type=user_type, university=teacher.access_object.university, creator=teacher)
			return redirect('manage_access_codes')
	else:
		form = GenerateCodeForm()
	return render(request, 'webapp/generate_access_codes.html', {'form' : form, 'teacher' : request.user})

"""View for teachers only for them to manage the access codes they generated."""
@login_required
def manage_access_codes(request):
	teacher = request.user
	access_codes = AccessCode.objects.filter(creator=teacher)
	unused_access_codes = access_codes.filter(user=None, user_type='Student')
	used_access_codes = access_codes.filter(user_type='Student').exclude(user=None)
	unused_teacher_access_codes = access_codes.filter(user=None, user_type='Teacher')
	used_teacher_access_codes = access_codes.filter(user_type='Teacher').exclude(user=None)
	return render(request, 'webapp/manage_access_codes.html', {
		'teacher' : teacher, 
		'unused_access_codes' : unused_access_codes, 
		'used_access_codes' : used_access_codes, 
		'unused_teacher_access_codes' : unused_teacher_access_codes, 
		'used_teacher_access_codes' : used_teacher_access_codes
		})


