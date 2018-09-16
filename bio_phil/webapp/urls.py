from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from bio_phil import settings
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('generate/', views.generate_access_codes, name='generate_access_codes'),
    path('manage/', views.manage_access_codes, name='manage_access_codes'),
    path('img_test',views.images,name ='image_tester'),
    staticfiles_urlpatterns(),
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    path('submit/', login_required(views.SubmitAnswer.as_view(template_name='webapp/submit.html')), name='submit'),
    path('submissions/', login_required(views.SubmissionList.as_view(template_name='webapp/submissions_list.html')), name='submissions_list'),
    path('submissions/<int:pk>/', login_required(views.EditAnswer.as_view()), name='edit')
]


