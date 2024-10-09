from django.db import models
from django.contrib.auth.models import UserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
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
    password = models.CharField(max_length=128, default='default_password')
    email = models.EmailField(unique=True, default=None)
    gender = models.CharField(max_length=1, choices=GENDER)
    profile_pic = models.ImageField(null=False, blank=False, default= 'images\avatar-trang-4.jpg' )
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()
    def __str__(self):
        return self.email 
    


class Session(models.Model):
    start_year = models.DateField()
    end_year = models.DateField()

    def __str__(self):
        return "From " + str(self.start_year) + " to " + str(self.end_year)

     
class Admin(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

class Subject(models.Model):
    name = models.CharField(max_length=120, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    profile = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    s_code = models.CharField(max_length=200, null= True, blank=True)

    def __str__(self):
        return self.profile.last_name + "  " + self.profile.first_name


class Staff(models.Model):
    profile = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.profile.first_name + " " + self.profile.last_name
    
class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam_type = models.CharField(max_length=100)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    def __str__(self):
        return f"{self.student} - {self.subject} - {self.score}"
    