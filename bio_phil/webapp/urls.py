from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('generate/', views.generate_access_codes, name='generate_access_codes'),
    path('manage/', views.manage_access_codes, name='manage_access_codes'),
]