from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.conf import settings

def send_verification_email(user, email, is_alert):
	mail_subject = 'Activate your account.'
	message = None
	if is_alert:
		message = render_to_string('webapp/acc_active_alert_email.html', {
			'user' : user,
			'default_domain' : settings.DEFAULT_DOMAIN,
			'uid' : urlsafe_base64_encode(force_bytes(user.pk)).decode(),
			'token' : account_activation_token.make_token(user),
		})
	else:
		message = render_to_string('webapp/acc_active_email.html', {
			'user' : user,
			'default_domain' : settings.DEFAULT_DOMAIN,
			'uid' : urlsafe_base64_encode(force_bytes(user.pk)).decode(),
			'token' : account_activation_token.make_token(user),
		})
	email_body = EmailMessage(mail_subject, message, to=[email])
	email_body.send()

def send_deletion_email(user):
	mail_subject = 'Your account has been deleted.'
	message = render_to_string('webapp/acc_active_alert_email.html', {
		'user' : user
	})
	email_body = EmailMessage(mail_subject, message, to=[user.email])
	email_body.send()