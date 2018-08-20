from django.shortcuts import render, get_object_or_404, redirect
from .forms import RegisterForm
from .models import User, AccessCode
from django.contrib.auth import authenticate, login, logout

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
