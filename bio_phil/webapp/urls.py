from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from bio_phil import settings
urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('generate/', views.generate_access_codes, name='generate_access_codes'),
    path('manage/', views.manage_access_codes, name='manage_access_codes'),
    path('img_test',views.images,name ='image_tester')
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)