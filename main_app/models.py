from django.db import models
from django.contrib.auth.models import UserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
import datetime
from decimal import Decimal
# Create your models here.

class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = CustomUser(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        assert extra_fields["is_staff"]
        assert extra_fields["is_superuser"]
        return self._create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    
    USER_TYPE = ((1, "HOD"),(2, "Staff") ,(3, "Student"))
    GENDER = [("M", "Male"), ("F", "Female")]

    username = None
    user_type = models.CharField(default=1, choices=USER_TYPE, max_length=1)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True, default=None)
    gender = models.CharField(max_length=1, choices=GENDER)
    profile_pic = models.ImageField(null=True, blank=True)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()
    def __str__(self):
        return self.email 

class Subject(models.Model):
    name = models.CharField(max_length=120, null=True, blank=True, default="Default Subject")
    code = models.CharField(max_length=20, default="SUB001")
    credit_number = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Department(models.Model):
    code = models.CharField(max_length=10, default="DEP001")
    name = models.CharField(max_length=50, default="Default Department")
    
    def __str__(self) -> str:
        return self.name
    
    
class ClassRoom(models.Model):
    name = models.CharField(max_length=50, default="Default Class Room")
    code = models.CharField(max_length=20, default="CLASS001")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, default=1)  # ID mặc định cho Department
    
    def __str__(self) -> str:
        return self.name

class Student(models.Model):
    profile = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    birth_day = models.DateField(default=datetime.date(2005, 12, 23))  # Ngày sinh mặc định
    code = models.CharField(max_length=20, default="STU001")
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, default=1)  # ID mặc định cho ClassRoom

    def __str__(self):
        return f"{self.profile.last_name} {self.profile.first_name}"

class Study_Section(models.Model):
    code = models.CharField(max_length=10, default="SEC001")
    name = models.CharField(max_length=50, default="Default Study Section")
    year = models.IntegerField(default=1)  # Năm học mặc định
    is_open = models.BooleanField(default=True, null= True, blank= True) # Trạng thái đăng ký
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, default=1)  # ID mặc định cho Subject
    
    def __str__(self) -> str:
        return self.name

class Lecturer(models.Model):
    profile = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, default=1)  
    study_section = models.ForeignKey(Study_Section, on_delete=models.CASCADE, null=True, blank=True)
    
    
    def __str__(self):
        return f"{self.profile.first_name} {self.profile.last_name}"
    
class Register(models.Model):
    SEMESTER_CHOICES = [
        ('1', 'Học kỳ 1'),
        ('2', 'Học kỳ 2'),
        ('3', 'Học kỳ 3'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)  
    study_section = models.ManyToManyField(Study_Section, blank=True)    
    enrollment_date = models.DateField(auto_now_add=True)  
    semester = models.TextField(default=1, choices= SEMESTER_CHOICES, max_length=1)
    midterm_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) 
    final_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  
    homework_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  
    def __str__(self):
        return f"{self.student.profile.last_name} - {', '.join([str(section) for section in self.study_section.all()])}"
    @property
    def Average(self):
        if self.homework_score==None or self.midterm_score==None or self.final_score==None:
            return None
        else:
            return self.homework_score * Decimal(0.1) + self.midterm_score * Decimal(0.4) + self.final_score * Decimal(0.5)
    


        
                                                             