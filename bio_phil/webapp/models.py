from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _
import string, secrets

USER_TYPE = (
	('Teacher', 'Teacher'),
	('Student', 'Student'),
)

class image_carousel(models.Model):
    img = models.ImageField(upload_to = 'media')
    pub_date = models.DateTimeField('Date Uploaded')

class AccessCode(models.Model):
	access_code = models.CharField(max_length=10)
	user_type = models.CharField(max_length=10, choices=USER_TYPE, default='Student')
	university = models.CharField(max_length=50)
	owner = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL, related_name='access_codes')

	def __str__(self):
		return self.access_code

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    access_object = models.OneToOneField(AccessCode, on_delete=models.SET_NULL, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

def random_code_generator(length):
	access_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(length))

	while(AccessCode.objects.filter(access_code=access_code).count() > 0):
		access_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(length))
		
	return access_code

