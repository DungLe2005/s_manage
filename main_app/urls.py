from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
   path('', views.gethome, name="home"),
   path('add_student/', views.add_student, name="add_student"),
   path('add_course/', views.add_course, name="add_course"),
   path('view_student/', views.view_student, name="view_student"),
]