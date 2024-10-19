from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name="home"),
    path('search/', views.search_view, name='search'),
    path('login/', views.login_page, name="login"),
    path('logout/', views.user_logout, name="logout"),
    #Department urls
    path('add_department/', views.add_department, name="add_department"),
    path('view_department/', views.view_department, name="view_department"),
    path('edit_department/<int:department_id>/', views.edit_department, name='edit_department'),
    path("delete_department/<int:department_id>",views.delete_department, name='delete_department'),
    #Classroom urls
    path('add_class/', views.add_class, name="add_class"),
    path('view_class/', views.view_class, name="view_class"),
    path('edit_class/<int:classroom_id>/', views.edit_class, name='edit_class'),
    path("delete_class/<int:classroom_id>",views.delete_class, name='delete_class'),
    #Student urls
    path('add_student/', views.add_student, name="add_student"),
    path('view_student/', views.view_student, name="view_student"),
    path("edit_student/<int:student_id>/",views.edit_student, name='edit_student'),
    path("delete_student/<int:student_id>",views.delete_student, name='delete_student'),
    #Lecturer urls
    path('add_lecturer/', views.add_lecturer, name="add_lecturer"),
    path('view_lecturer/', views.view_lecturer, name="view_lecturer"),
    path("edit_lecturer/<int:lecturer_id>/",views.edit_lecturer, name='edit_lecturer'),
    path("delete_lecturer/<int:lecturer_id>",views.delete_lecturer, name='delete_lecturer'),
    #Subject urls
    path('add_subject/', views.add_subject, name="add_subject"),
    path('view_subject/', views.view_subject, name="view_subject"),
    path('edit_subject/<int:subject_id>/', views.edit_subject, name='edit_subject'),
    path("delete_subject/<int:subject_id>",views.delete_subject, name='delete_subject'),
    #Study_Section urls
    path('add_studysection/', views.add_studysection, name="add_studysection"),
    path('view_studysection/', views.view_studysection, name="view_studysection"),
    path('edit_studysection/<int:studysection_id>/', views.edit_studysection, name='edit_studysection'),
    path("delete_studysection/<int:studysection_id>",views.delete_studysection, name='delete_studysection'),
    
    #Register urls
    path('register/<int:student_id>/', views.register, name='register'),
    path('view_register/<int:student_id>/', views.view_register, name='view_register'),
    
    
    path('add_grade/<int:registration_id>/',views.add_grade, name='add_grade'),
    path('view_grade/', views.view_grade, name="view_grade"),
    # path('edit_grade/<int:grade_id>/', views.edit_grade, name='edit_grade'),
    # path("delete_grade/<int:grade_id>",views.delete_grade, name='delete_grade'),
]