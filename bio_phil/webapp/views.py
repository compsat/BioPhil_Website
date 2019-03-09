from django.shortcuts import render, get_object_or_404, redirect
from .forms import RegisterForm, GenerateCodeForm, ChangePasswordForm, LoginForm, ChangeEmailForm, ResendForm, SubmitForm
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
import os, tempfile, zipfile, mimetypes, io
from wsgiref.util import FileWrapper
from django.http import HttpResponse

def index(request):
	message = None
	message_type = None
	if 'message' in request.session:
		message = request.session['message']
		message_type = request.session['message_type']
		del request.session['message']
		del request.session['message_type']
	modules_list = Module.objects.all().order_by('id')[:3]
	return render(request, 'webapp/index.html', {'message' : message, 'message_type' : message_type, 'modules_list' : modules_list})

"""
View for a user's profile where they can change their password.
"""
@login_required
def profile(request):
	user = request.user
	submissions_list = Submission.objects.filter(user=user)
	messages = None
	message_type = None
	if request.method == 'POST':
		if 'new_password1' in request.POST:
			change_password = ChangePasswordForm(user, request.POST)
			change_email = ChangeEmailForm(request=request)
			submit_form = SubmitForm()
			if change_password.is_valid():
				user = change_password.save()
				update_session_auth_hash(request, user)
				messages = 'Your password was successfully updated!'
				message_type = "success"
			else:
				messages = "There was an error while updating your password."
				message_type = "danger"
		elif 'new_email' in request.POST:
			change_password = ChangePasswordForm(user)
			change_email = ChangeEmailForm(request.POST, request=request)
			submit_form = SubmitForm()
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
				messages = 'An email was sent to your old email and your desired new email. Please check either of them to confirm your update.'
				message_type = 'primary'
			else:
				messages = "There was an error while updating your email."
				message_type = 'danger'
		elif 'edit-response' in request.POST:
			change_password = ChangePasswordForm(user)
			change_email = ChangeEmailForm(request=request)
			submit_form = SubmitForm(request.POST, request.FILES)

			submission_pk = request.POST['submission-id']
			if submit_form.is_valid():
				submission = Submission.objects.get(pk=submission_pk)
				submission_form = submit_form.save(commit=False)
				submission.file = submission_form.file
				submission.save()
				messages = "Your submission has been edited!"
				message_type = "success"
			else:
				messages = "There was an error in submitting an answer."
				message_type = "danger"
	else:
		change_password = ChangePasswordForm(user)
		change_email = ChangeEmailForm(request=request)
		submit_form = SubmitForm()
	return render(request, 'webapp/profile_page.html', {
		'change_password' : change_password, 
		'change_email' : change_email,  
		'user' : user, 
		'messages' : messages,
		'message_type' : message_type,
		'submissions_list' : submissions_list,
		'submit_form' : submit_form
		})

def resend_verification(request):
	if request.method == 'POST':
		form = ResendForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
			user = User.objects.get(email=email)
			send_verification_email(user, email, False)
			request.session['message'] = 'Please check your email to verify your account and complete the registration. If you do not \
				verify by {} GMT+8, your account will be deleted.'.format(user.expiration_date.strftime("%B %d, %Y %I:%M %p"))
			request.session['message_type'] = 'primary'
			return redirect('index')
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
		request.session['message'] = 'You have successfully changed your email. You may now login using your new email.'
		request.session['message_type'] = 'success'
	else:
		request.session['message'] = 'Email update link is invalid!'
		request.session['message_type'] = 'danger'
	return redirect('index')

def confirm(request):
	if 'email' in request.session:
		email = request.session['email']
		first_name = request.session['first_name']
		last_name = request.session['last_name']
		password1 = request.session['password1']
		access_field = request.session['access_field']
		access_object = AccessCode.objects.get(access_code=access_field)

		if request.method == 'POST':
			if 'confirm_reg' in request.POST:
				user = User.objects.create(email=email, first_name=first_name, last_name=last_name, access_object=access_object)
				user.set_password(password1)
				user.is_active = False
				user.save()
				del request.session['email']
				del request.session['first_name']
				del request.session['last_name']
				del request.session['password1']
				del request.session['access_field']
				send_verification_email(user, email, False)
				request.session['message'] = 'Please check your email to verify your account and complete the registration. If you do not \
					verify by {} GMT+8, your account will be deleted.'.format(user.expiration_date.strftime("%B %d, %Y %I:%M %p"))
				request.session['message_type'] = 'primary'
				return redirect('index')
			elif 'go_back' in request.POST:
				request.session['initial_data'] = {
					'email' : email,
					'first_name' : first_name,
					'last_name' : last_name,
					'access_field' : access_field,
				}
				del request.session['email']
				del request.session['first_name']
				del request.session['last_name']
				del request.session['password1']
				del request.session['access_field']
				return redirect('register')

		context = {'first_name' : first_name, 'last_name':last_name, 'email': email, 'university' : access_object.university, 'user_type' : access_object.user_type}
		return render(request, 'webapp/confirmation.html', context)

	else:
		return redirect('register')

def register(request):
	if request.user.is_authenticated:
		return redirect('index')
	else:
		if request.method == 'POST':
			form = RegisterForm(request.POST)
			if form.is_valid():
				request.session['email'] = request.POST['email']
				request.session['first_name'] = request.POST['first_name']
				request.session['last_name'] = request.POST['last_name']
				request.session['password1'] = request.POST['password1']
				request.session['access_field'] = request.POST['access_field']
				return redirect('conf_reg')
		else:
			form = RegisterForm()

			if 'initial_data' in request.session:
				form = RegisterForm(initial=request.session['initial_data'])
				del request.session['initial_data']

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
		request.session['message'] = 'Thank you for your email confirmation. You can now login your account.'
		request.session['message_type'] = 'success'
	else:
		request.session['message'] = 'Activation link is invalid!'
		request.session['message_type'] = 'danger'
	return redirect('index')

"""View for teachers to view all the submissions of the students"""
def submissions(request):
	if request.user.access_object.user_type == 'Student':
		request.session['message'] = 'Only teachers can view this page.'
		request.session['message_type'] = 'warning'
		return redirect('index')

	submissions_list = Submission.objects.all()
	return render(request, 'webapp/submissions_list.html', {'user' : request.user, 'submissions_list' : submissions_list})

"""View for teachers only for them to generate a specified number of access codes
either for their students or fellow teachers"""
@login_required
def generate_access_codes(request):
	access_objects = AccessCode.objects.filter(creator=request.user)
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
			return render(request, 'webapp/generate_access_codes.html', {'form' : form, 'teacher' : request.user, 'access_objects' : access_objects, 'messages' : "Successfully generated access codes!"})
	else:
		form = GenerateCodeForm()
	return render(request, 'webapp/generate_access_codes.html', {'form' : form, 'teacher' : request.user, 'access_objects' : access_objects})

#View for image_carousel model
# def images(request):
# 	image_list = image_carousel.objects.order_by('-id')[:5]
# 	context = {'image_list':image_list}
# 	return render(request, 'webapp/img_carousel_test.html',context)

def module(request):
	modules_list = Module.objects.all()
	message = None
	message_type = None
	if request.method == 'POST':
		if 'add-response' in request.POST:
			module_id = request.POST['module-id']
			submit_form = SubmitForm(request.POST, request.FILES)
			if submit_form.is_valid():
				module = Module.objects.get(pk=module_id)
				submission = submit_form.save(commit=False)
				submission.module = module
				submission.user = request.user
				submission.save()
				message = "Successfully submitted an answer!"
				message_type = 'success'
			else:
				message = "There was an error in submitting an answer."
				message_type = 'danger'

		elif 'edit-response' in request.POST:
			submit_form = SubmitForm(request.POST, request.FILES)
			submission_pk = request.POST['submission-id']
			if submit_form.is_valid():
				submission = Submission.objects.get(pk=submission_pk)
				submission_form = submit_form.save(commit=False)
				submission.file = submission_form.file
				submission.save()
				message = "Your submission has been edited!"
				message_type = 'success'
			else:
				message = "There was an error in submitting an answer."
				message_type = 'danger'
	else:
		submit_form = SubmitForm()

	context = {'modules_list': modules_list, 'user' : request.user, 'message' : message, 'message_type' : message_type, 'submit_form': submit_form}
	return render(request, 'webapp/modules.html', context)

def send_file(request, file_name):
    filename = os.path.join(settings.MEDIA_ROOT, file_name)
    wrapper = FileWrapper(open(filename, 'rb'))
    content_type = mimetypes.guess_type(filename)[0]
    response = HttpResponse(wrapper, content_type=content_type)
    response['Content-Length'] = os.path.getsize(filename)    
    response['Content-Disposition'] = "attachment; filename=%s"%file_name
    return response

def send_zip(request, module_id):
	from io import BytesIO
	module = Module.objects.get(pk=module_id)
	filenames = []
	for download in module.downloads.all():
		filenames.append(os.path.join(settings.MEDIA_ROOT, download.file.name))

	byte_data = BytesIO()
	zip_file = zipfile.ZipFile(byte_data, "w")

	for file in filenames:
		filename = os.path.basename(os.path.normpath(file))
		zip_file.write(file, filename)
	zip_file.close()

	response = HttpResponse(byte_data.getvalue(), content_type='application/zip')
	response['Content-Disposition'] = 'attachment; filename={}.zip'.format(module.title)

	return response

def render_gallery(request):
	modules = Module.objects.all()
	context = {'modules': modules}
	temp = {}
	for module in modules:
		temp[module.id] = ModuleImage.objects.filter(module_id=module.id)
		context['images'] = temp
	
	return render(request, "webapp/gallery.html", context)