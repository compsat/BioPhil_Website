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
					access_object = AccessCode.objects.get(access_code=access_code)
					user.access_object = access_object
					user.save()
					login(request, user)
					return redirect('index')
	else:
		form = RegisterForm()
	return render(request, 'webapp/signup.html', {'form' : form})

@login_required
def generate_access_codes(request):
	if request.method == 'POST':
		teacher = request.user
		form = GenerateCodeForm(request.POST)
		if form.is_valid():
			access_object = form.save(commit=False)
			quantity = form.cleaned_data['quantity']
			access_object.access_code = random_code_generator(5)
			access_object.user_type = 'Student'
			access_object.university = teacher.access_object.university
			access_object.owner = teacher
			access_object.save()
			for x in range(1, quantity):
				access_code = random_code_generator(5)
				obj = AccessCode.objects.create(access_code=access_code, user_type='Student', university=teacher.access_object.university, owner=teacher)
			return redirect('manage_access_codes')
	else:
		form = GenerateCodeForm()
	return render(request, 'webapp/generate_access_codes.html', {'form' : form, 'teacher' : request.user})

@login_required
def manage_access_codes(request):
	teacher = request.user
	access_codes = AccessCode.objects.filter(owner=teacher)
	unused_access_codes = access_codes.filter(user=None)
	used_access_codes = access_codes.exclude(user=None)
	return render(request, 'webapp/manage_access_codes.html', {'teacher' : teacher, 'unused_access_codes' : unused_access_codes, 'used_access_codes' : used_access_codes})