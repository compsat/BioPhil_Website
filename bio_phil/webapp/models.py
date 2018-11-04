from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _
from datetime import timedelta
from django.utils import timezone
from webapp.tasks import *
import os

USER_TYPE = (
	('Teacher', 'Teacher'),
	('Student', 'Student'),
)

class AccessCode(models.Model):
	access_code = models.CharField(max_length=10)
	user_type = models.CharField(max_length=10, choices=USER_TYPE, default='Student')
	university = models.CharField(max_length=50)
	creator = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL, related_name='access_codes')
    

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
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()
    
    @property
    def expiration_date(self):
        return self.created_at + timedelta(days=30)

    def save(self, *args, **kwargs):
        do_tasks = False
        if self.pk is None: 
            do_tasks = True

        super(User, self).save(*args, **kwargs)

        if do_tasks:
            alert_inactive_user(self.pk)
            delete_inactive_user(self.pk)

class NewEmail(models.Model):
    email_code = models.CharField(max_length=20, unique=True)
    new_email = models.EmailField()
    old_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.get_full_name() + ": " + self.new_email
    
class Updates(models.Model):# to get the last 5 in the query, order it by ID number in descending order, then get [0:4]
    update_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField(verbose_name='Date Published')
    test = models.CharField(max_length = 10)

    def __str__(self):
        return self.update_text

    class Meta:
    	ordering = ('pub_date',)

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='submissions')
    module = models.ForeignKey('Module', on_delete=models.DO_NOTHING)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return "Module # - " + self.user.get_full_name()
    
    class Meta:
        ordering = ('created_at',)

class ImageCarousel(models.Model):
    img = models.ImageField(upload_to='images')
    img_name = models.CharField(max_length=30)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.img_name

class Module(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    module_summary = models.CharField(max_length=300)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class ModuleImage(models.Model):
    image = models.ImageField(upload_to = 'module/images')
    img_name = models.CharField(max_length = 30)
    pub_date = models.DateTimeField(auto_now_add = True)
    module = models.ForeignKey(Module, on_delete=models.DO_NOTHING, related_name='images', blank=True, null=True)

    def __str__(self):
        return self.img_name

class Download(models.Model):
    title = models.CharField(max_length=120, unique=True)
    module = models.ForeignKey('Module', on_delete=models.CASCADE, related_name='downloads', blank=True, null=True)
    file = models.FileField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension[1:]

    def file_size(self):
        """Returns the filesize of the filename given in value"""
        return self.file.size

class DeletionLog(models.Model):
    email = models.EmailField()
    full_name = models.CharField(max_length=200)
    access_code = models.CharField(max_length=10)
    user_created_at = models.DateTimeField()
    deleted_at = models.DateTimeField(auto_now_add=True)