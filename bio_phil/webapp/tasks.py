# Create your tasks here
# from __future__ import absolute_import, unicode_literals
# from celery import shared_task
from webapp.helper_methods import send_verification_email, send_deletion_email
from datetime import timedelta
from background_task import background
import webapp

@background(schedule=timedelta(days=14))
# @shared_task
def alert_inactive_user(user_id):
	user = webapp.models.User.objects.get(pk=user_id)
	print("TASK DONE")
	if not user.is_active:
		print("EMAIL SENT")
		send_verification_email(user, user.email, True)

@background(schedule=timedelta(days=30))
# @shared_task
def delete_inactive_user(user_id):
	# lookup user by id and send them a message
	user = webapp.models.User.objects.get(pk=user_id)
	if not user.is_active:
		email = user.email
		full_name = user.get_full_name()
		access_code = user.access_object.access_code
		user_created_at = user.created_at
		send_deletion_email(user)
		webapp.models.DeletionLog.objects.create(email=email, full_name=full_name, access_code=access_code, user_created_at=user_created_at)
		user.delete()