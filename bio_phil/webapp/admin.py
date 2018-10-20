from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _
from .models import *
from . import forms

# Register your models here.
@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password', 'access_object')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'university', 'is_staff')
    list_filter = ('access_object__user_type', 'access_object__university')
    search_fields = ('email', 'first_name', 'last_name',)
    ordering = ('email',)

    def university(self, x):
        if x.access_object:
            return x.access_object.university

    def user_type(self, x):
        if x.access_object:
            return x.access_object.user_type

class UserInline(admin.StackedInline):
    model = User
    fields = ('email',)

class AccessCodeAdmin(admin.ModelAdmin):
    list_display = ('access_code', 'user_type', 'university', 'user')
    list_filter = ('user_type', 'university')
    inlines = []
    readonly_fields = ('creator',)

    def user(self, x):
        return x.user
    user.short_description = 'user'

    def add_view(self, request, extra_content=None):
        self.form = forms.AdminAccessCodeAddForm
        self.inlines = []
        return super(AccessCodeAdmin, self).add_view(request)

    def change_view(self, request, object_id, extra_content=None):
        self.form = forms.AdminAccessCodeChangeForm
        self.inlines = [UserInline]
        return super(AccessCodeAdmin, self).change_view(request, object_id)

    def save_model(self, request, obj, form, change):
        user_type = obj.user_type
        university = obj.university
        quantity = form.cleaned_data.get('quantity')
        for x in range(0, quantity):
            obj.access_code = random_code_generator(5)
            super(AccessCodeAdmin, self).save_model(request, obj, form, change)
            if x != (quantity-1):
                obj = AccessCode.objects.create(user_type=user_type, university=university)

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'module', 'university', 'created_at', 'updated_at')
    list_filter = ('module', 'user__last_name', 'user__access_object__university', 'created_at')
    readonly_fields = ('created_at', 'updated_at')

    def full_name(self, x):
        return x.user.get_full_name()
    full_name.short_description = 'Full Name'

    def university(self, x):
        return x.user.access_object.university

class DownloadInline(admin.StackedInline):
    model = Download
    fields = ('title', 'file')

class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [
        DownloadInline,
    ]


class DownloadAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'file', 'created_at')
    list_filter = ('module', 'created_at')
    readonly_fields = ('created_at',)

admin.site.register(AccessCode, AccessCodeAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(image_carousel)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Download, DownloadAdmin)