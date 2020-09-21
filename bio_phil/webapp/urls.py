from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from bio_phil import settings
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.urls import static


urlpatterns = [
    path('', views.index, name='index'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('gallery/', views.render_gallery, name='gallery'),
    path('generate/', views.generate_access_codes, name='generate_access_codes'),
    path('media/<str:file_name>/', views.send_file, name='send_file'),
    path('media/module_zip/<int:module_id>/', views.send_zip, name='send_zip'),
    path('modules/', login_required(views.module), name='modules'),
    path('my_profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    path('register/confirm_reg/',views.confirm, name='conf_reg'),
    path('resend_verification/', views.resend_verification, name='resend_verification'),
    path('submissions/', login_required(views.submissions), name='submissions_list'),
    path('update_email/<uidb64>/<token>/<email_code>', views.update_email, name='update_email'),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_DIR, document_root=settings.MEDIA_ROOT)
