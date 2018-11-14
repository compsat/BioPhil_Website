from django import template

register = template.Library()

@register.simple_tag
def user_submission(user, module):
	for submission in user.submissions.all():
		if module == submission.module:
			return submission

	return None