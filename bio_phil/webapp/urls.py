from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from bio_phil import settings
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', views.index, name='index'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('gallery/', views.gallery, name='gallery'),
    path('generate/', views.generate_access_codes, name='generate_access_codes'),
    # path('img_test',views.images,name ='image_tester'),
    path('media/<str:file_name>/', views.send_file, name='send_file'),
    path('modules/', login_required(views.module), name='modules'),
    path('my_profile/', views.profile, name='profile'),
    path('submissions/', login_required(views.SubmissionList.as_view(template_name='webapp/submissions_list.html')), name='submissions_list'),
    path('submit/', login_required(views.SubmitAnswer.as_view(template_name='webapp/submit.html')), name='submit'),
    path('register/', views.register, name='register'),
    path('register/confirm_reg/',views.confirm, name='conf_reg'),
    path('resend_verification/', views.resend_verification, name='resend_verification'),
    path('update_email/<uidb64>/<token>/<email_code>', views.update_email, name='update_email'),
]