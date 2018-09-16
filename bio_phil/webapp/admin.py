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
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

class UserInline(admin.StackedInline):
    model = User
    fields = ('email',)

class AccessCodeAdmin(admin.ModelAdmin):
    list_display = ('access_code', 'user_type', 'university', 'user')
    list_filter = ('user_type', 'university')
    inlines = []
    readonly_fields = ('owner',)

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

admin.site.register(AccessCode, AccessCodeAdmin)
admin.site.register(image_carousel)