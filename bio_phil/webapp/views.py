from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .forms import RegisterForm, GenerateCodeForm, ChangePasswordForm, LoginForm, ChangeEmailForm, ResendForm
from .models import *
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.auth import views as auth_views
from .helper_methods import send_verification_email, random_code_generator
from django.conf import settings

def index(request):
	# update_text = Updates.object.all()[0:4]
#     context = {'update_text':update_text}
#     return render(<insert html file name here pls ty =D>, context)
	return render(request, 'webapp/index.html')

"""
View for a user's profile where they can change their password.
"""
@login_required
def profile(request):
	user = request.user
	messages = None
	if request.method == 'POST':
		if 'password1' in request.POST:
			change_password = ChangePasswordForm(user, request.POST)
			# change_email = ChangeEmailForm()
			if change_password.is_valid():
				user = change_password.save()
				update_session_auth_hash(request, user)
				messages = 'Your password was successfully updated!'
				return render(request, 'webapp/profile_page.html', {'change_password' : change_password, 'user' : user, 'messages' : messages})
				# return render(request, 'webapp/profile_page.html', {'change_password' : change_password, 'change_email' : change_email, 'user' : user, 'messages' : messages})
		elif 'new_email' in request.POST:
			change_email = ChangeEmailForm(request.POST, request=request)
			if change_email.is_valid():
				old_email = user.email
				new_email_object = change_email.save(commit=False)
				new_email = change_email.cleaned_data['new_email']
				new_email_object.new_email = new_email
				new_email_object.old_email = old_email
				new_email_object.user = user
				email_code = random_code_generator(10, 'new_email')
				new_email_object.email_code = email_code
				new_email_object.save()

				mail_subject = 'Update your email address.'
				message = render_to_string('webapp/acc_update_email.html', {
					'user' : user,
					'default_domain' : settings.DEFAULT_DOMAIN,
					'uid' : urlsafe_base64_encode(force_bytes(user.pk)).decode(),
					'token' : account_activation_token.make_token(user),
					'old_email' : old_email,
					'new_email' : new_email,
					'email_code' : email_code
				})
				email_body = EmailMessage(mail_subject, message, to=[old_email, new_email])
				email_body.send()

				return HttpResponse('An email was sent to your old email and your desired new email. Please check either of them to confirm your update.')
	else:
		change_password = ChangePasswordForm(user)
		change_email = ChangeEmailForm(request=request)
		# change_email.fields['old_email'].initial = user.email
	return render(request, 'webapp/profile_page.html', {'change_password' : change_password, 'change_email' : change_email,  'user' : user, 'messages' : messages})

def resend_verification(request):
	if request.method == 'POST':
		form = ResendForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
			user = User.objects.get(email=email)
			send_verification_email(user, email, False)
			return HttpResponse('Please verify your email address to complete the registration. If you do not \
				verify by {}, your account will be deleted.'.format(user.expiration_date))
	else:
		form = ResendForm()
	return render(request, 'webapp/send_verification.html', {'form' : form})

def update_email(request, uidb64, token, email_code):
	try:
		# uid = force_text(urlsafe_base64_decode(uidb64))
		uid = urlsafe_base64_decode(uidb64).decode()
		user = User.objects.get(pk=uid)
	except(TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None

	if user is not None and account_activation_token.check_token(user, token):
		logout(request)
		email_object = NewEmail.objects.get(email_code=email_code)
		user.email = email_object.new_email
		user.save()
		return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
	else:
		return HttpResponse('Activation link is invalid!')

def register(request):
	if request.method == 'POST':
		form = RegisterForm(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			email = form.cleaned_data['email']
			password = form.cleaned_data['password1']
			access_code = form.cleaned_data['access_field']
			user.set_password(password)
			user.is_active = False
			"""Attaches an access_object to the user based on the inputted access code"""
			access_object = AccessCode.objects.get(access_code=access_code)
			user.access_object = access_object
			user.save()
			
			send_verification_email(user, email, False)
			return HttpResponse('Please verify your email address to complete the registration. If you do not \
				verify by {}, your account will be deleted.'.format(user.expiration_date))
	else:
		form = RegisterForm()
	return render(request, 'webapp/signup.html', {'form' : form})

def activate(request, uidb64, token):
	try:
		# uid = force_text(urlsafe_base64_decode(uidb64))
		uid = urlsafe_base64_decode(uidb64).decode()
		user = User.objects.get(pk=uid)
	except(TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None

	if user is not None and account_activation_token.check_token(user, token):
		logout(request)
		user.is_active = True
		user.save()
		return HttpResponse('Thank you for your email confirmation. You can now login your account.')
	else:
		return HttpResponse('Activation link is invalid!')

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
			access_object.access_code = random_code_generator(5, 'access_code')
			access_object.user_type = user_type
			access_object.university = teacher.access_object.university
			access_object.creator = teacher
			access_object.save()
			for x in range(1, quantity):
				access_code = random_code_generator(5, 'access_code')
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
	context = {'module_list': module_list}
	return render(request, 'webapp/module_tester.html', context)