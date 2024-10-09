from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.gethome, name="home"),
    path('login/', views.login_page, name="login"),
    path('add_student/', views.add_student, name="add_student"),
    path('add_course/', views.add_course, name="add_course"),
    path('add_grade/', views.add_grade, name="add_grade"),
    path('add_staff/', views.add_staff, name="add_staff"),
    path('view_student/', views.view_student, name="view_student"),
    path('view_staff/', views.view_staff, name="view_staff"),
    path('view_subject/', views.view_subject, name="view_subject"),
    path('view_grade/', views.view_grade, name="view_grade"),
    path('edit_subject/<int:subject_id>/', views.edit_subject, name='edit_subject'),
    path("delete_subject/<int:subject_id>",views.delete_subject, name='delete_subject'),
    path("delete_/<int:subject_id>",views.delete_subject, name='delete_subject'),

]