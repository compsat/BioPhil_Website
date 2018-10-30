from django.shortcuts import render, get_object_or_404, redirect
from .forms import RegisterForm, GenerateCodeForm, ChangePasswordForm
from .models import *
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

def index(request):
	if request.method == 'POST':
		form = RegisterForm(request.POST)
		if form.is_valid():
			print('form is valid')
			user = form.save(commit=False)
			email = form.cleaned_data['email']
			password = form.cleaned_data['password1']
			access_code = form.cleaned_data['access_field']
			user.set_password(password)
			user.save()
			user = authenticate(email=email, password=password)
			print('user is saved!')
			if user is not None:
				if user.is_active:
					"""Attaches an access_object to the user based on the inputted access code"""
					access_object = AccessCode.objects.get(access_code=access_code)
					user.access_object = access_object
					user.save()
					print('user is saved!')
					# login(request, user)
					# return redirect('index')
	return render(request, 'webapp/index.html')

"""
View for a user's profile where they can change their password.
"""
@login_required
def profile(request):
	user = request.user
	messages = None
	if request.method == 'POST':
		if 'old_password' in request.POST:
			change_password = ChangePasswordForm(user, request.POST)
			# change_email = ChangeEmailForm()
			if change_password.is_valid():
				user = change_password.save()
				update_session_auth_hash(request, user)
				messages = 'Your password was successfully updated!'
				return render(request, 'webapp/profile_page.html', {'change_password' : change_password, 'user' : user, 'messages' : messages})
				# return render(request, 'webapp/profile_page.html', {'change_password' : change_password, 'change_email' : change_email, 'user' : user, 'messages' : messages})
		# elif 'change_password' in request.POST:
		# 	change_password = ChangePasswordForm(use, request.POST)
		# 	if form.is_valid():
		# 		user = form.save()
	 #            update_session_auth_hash(request, user)  # Important!
	 #            messages.success(request, 'Your password was successfully updated!')
	 #            return redirect('profile')
	else:
		change_password = ChangePasswordForm(user)
		# change_email = ChangeEmailForm()
	return render(request, 'webapp/profile_page.html', {'change_password' : change_password, 'user' : user, 'messages' : messages})
	# return render(request, 'webapp/profile_page.html', {'change_password' : change_password, 'change_email' : change_email, 'user' : user, 'messages' : messages})

def confirm(request):
	form = RegisterForm(request.POST)
	if form.is_valid:
		first_name = request.POST.get('first_name')
		last_name = request.POST.get('last_name')
		email_add = request.POST.get('email')
		password = request.POST.get('password1')
		access_code_number = request.POST.get('access_field')
		access_code1 = AccessCode.objects.get(access_code = access_code_number)
		school = access_code1.university
		usertype = access_code1.user_type
		init = {'first_name':first_name, 'last_name':last_name, 'email': email_add, 'school':school, 'usertype':usertype, 'access_field': access_code_number,'password1':password,'password2':password}
		form = RegisterForm(initial = init)
		form.fields['password1'].widget.render_value = True
		form.fields['password2'].widget.render_value = True		
		context = {'first_name':first_name, 'last_name':last_name, 'email_add': email_add, 'school':school, 'usertype':usertype, 'access_field': access_code_number,'form':form}
		return render(request, 'webapp/signup_confirm.html',context)
	# else:
	# 	form = RegisterForm(request.GET)
	# 	if form.is_valid():
	# 		print('form is valid')
	# 		user = form.save(commit=False)
	# 		email = form.cleaned_data['email']
	# 		password = form.cleaned_data['password1']
	# 		access_code = form.cleaned_data['access_field']
	# 		user.set_password(password)
	# 		user.save()
	# 		user = authenticate(email=email, password=password)
	# 		if user is not None:
	# 			if user.is_active:
	# 				"""Attaches an access_object to the user based on the inputted access code"""
	# 				access_object = AccessCode.objects.get(access_code=access_code)
	# 				user.access_object = access_object
	# 				user.save()
	# 				login(request, user)
	# 				return redirect('index')

	# first_name = request.POST.get('first_name')
	# last_name = request.POST.get('last_name')
	# email_add = request.POST.get('email')
	# password = request.POST.get('password1')
	# access_code_number = request.POST.get('access_field')
	# access_code1 = AccessCode.objects.get(access_code = access_code_number)
	# school = access_code1.university
	# usertype = access_code1.user_type
	# init = {'first_name':first_name, 'last_name':last_name, 'email': email_add, 'school':school, 'usertype':usertype, 'access_field': access_code_number,'password1':password,'password2':password}
	# form = RegisterForm(initial = init)
	# form.fields['password1'].widget.render_value = True
	# form.fields['password2'].widget.render_value = True
	
	# context = {'first_name':first_name, 'last_name':last_name, 'email_add': email_add, 'school':school, 'usertype':usertype, 'access_field': access_code_number,'form':form}
	# return render(request, 'webapp/signup_confirm.html',context)

def register(request):
	form = RegisterForm()
	return render(request, 'webapp/signup.html', {'form' : form})

"""View for students to view their submissions to all modules OR for teachers
to view all the submissions of the students"""
class SubmissionList(ListView):
	model = Submission
	paginate_by = 50

	def get_context_data(self, **kwargs):
		context = super(SubmissionList, self).get_context_data(**kwargs)
		context['user'] = self.request.user
		context['submissions_list'] = self.get_queryset()
		return context

	def get_queryset(self):
		queryset = Submission.objects.all()
		if self.request.user.access_object.user_type == 'Student':
			queryset = queryset.filter(user=self.request.user)

		return queryset

"""View for students to submit their answers to modules"""
class SubmitAnswer(CreateView):
	model = Submission
	fields = ['module', 'answer']
	success_url = reverse_lazy('submissions_list')

	def form_valid(self, form):
		form.instance.user = self.request.user
		return super().form_valid(form)

"""View for students to edit their answers to modules"""
class EditAnswer(UpdateView):
	model = Submission
	fields = ['answer']
	success_url = reverse_lazy('submissions_list')
	template_name_suffix = '_update_form'

	def get_context_data(self, **kwargs):
		context = super(EditAnswer, self).get_context_data(**kwargs)
		context['user'] = self.request.user
		context['module'] = self.object.module
		return context

	def get_queryset(self):
		queryset = Submission.objects.all()
		if self.request.user.access_object.user_type == 'Student':
			queryset = queryset.filter(user=self.request.user)

		return queryset

"""View for students to delete their answers to modules"""
class DeleteAnswer(DeleteView):
	model = Submission
	success_url = reverse_lazy('submissions_list')

	def get_queryset(self):
		queryset = Submission.objects.all()
		if self.request.user.access_object.user_type == 'Student':
			queryset = queryset.filter(user=self.request.user)

		return queryset

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
	access_codes = AccessCode.objects.filter(owner=teacher)
	unused_access_codes = access_codes.filter(user=None)
	used_access_codes = access_codes.exclude(user=None)
	return render(request, 'webapp/manage_access_codes.html', {'teacher' : teacher, 'unused_access_codes' : unused_access_codes, 'used_access_codes' : used_access_codes})

# View for the update model. 

# def updates(request):
#     update_text = Updates.object.all()[0:5]
#     context = {'update_text':update_text}
#     return render(<insert html file name here pls ty =D>, context)

#View for image_carousel model
def images(request):
	image_list = image_carousel.objects.order_by('-id')[:5]
	context = {'image_list':image_list}
	return render(request, 'webapp/img_carousel_test.html',context)

def module(request):
	module_list = Module.objects.all()
	context = {'module_list': module_list,}
	return render(request, 'webapp/module_tester.html', context)