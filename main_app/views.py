from django.http import JsonResponse
import requests
from django.shortcuts import render, redirect
from .forms import *
from django.http import HttpResponse
from .models import *
from django.contrib import messages
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
# Create your views here.

def login_page(request):
    if request.user.is_authenticated:
        if request.user.user_type == "1":
            return redirect(reverse("admin_home"))
        elif request.user.user_type == "2":
            return redirect(reverse("staff_home"))
        else:
            return redirect(reverse("student_home"))
    return render(request, "main_app/login.html")

def gethome(request):
    return render(request,"hod_templates/home.html")

def add_student(request):
    if request.method == "POST":
        student_form = StudentForm(request.POST, request.FILES)
        if student_form.is_valid():
            email = student_form.cleaned_data.get("email")
            # Kiểm tra xem email đã tồn tại hay chưa
            if CustomUser.objects.filter(email=email).exists():
                 return JsonResponse({"status": "error", "message": "Email đã được đăng ký"}, status=400)
            else:
                try:
                    first_name = student_form.cleaned_data.get("first_name")
                    last_name = student_form.cleaned_data.get("last_name")
                    s_code = student_form.cleaned_data.get("s_code")
                    gender = student_form.cleaned_data.get("gender")
                    address = student_form.cleaned_data.get("address")
                    password = student_form.cleaned_data.get("password")
                    subject = student_form.cleaned_data.get("subject")
                    print(f'mã subject: {subject}')
                    passport = request.FILES["profile_pic"]

                    # Lưu hình ảnh
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)

                    # Tạo người dùng
                    user = CustomUser.objects.create_user(
                        email=email,
                        password=password,
                        user_type=3,
                        first_name=first_name,
                        last_name=last_name,
                        profile_pic=passport_url,
                    )

                    # Tạo sinh viên
                    student = Student(profile=user, subject=subject, s_code=s_code)
                    student.save()

                    # Cập nhật thông tin người dùng
                    user.gender = gender
                    user.address = address
                    user.save()
                    # return JsonResponse({"status": "success", "message": "Đã thêm thành công"}, status=201)
                    messages.success(request, 'Thêm sinh viên thành công')
                    return redirect('add_student')
                except Exception as e:
                    messages.success(request, 'Lỗi 500 không thể thêm sinh viên')
                    return redirect('add_student')
        else:
            errors = student_form.errors.as_json()
            return render(request, 'hod_templates/add_student.html')
    else:
        student_form = StudentForm()  # Khởi tạo form trống khi GET
        return render(request, 'hod_templates/add_student.html', {'form': student_form})

        # return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)
    

def add_course(request):
    form = CourseForm(request.POST or None)
    context = {"form": form, "page_title": "Thêm khóa học"}
    if request.method == "POST":
        if form.is_valid():
            name = form.cleaned_data.get("name")
            try:
                course = Subject()
                course.name = name
                course.save()
                messages.success(request, "Đã thêm thành công")
                return redirect(reverse("add_course"))
            except:
                messages.error(request, "Could Not Add")
        else:
            messages.error(request, "Could Not Add")
    return render(request, "hod_templates/add_course.html", context)


def view_student(request):
    students = Student.objects.select_related('profile').all()  # Lấy tất cả sinh viên từ model Student
    
    if not students.exists():
        print("Không tìm thấy sinh viên nào.")  # Kiểm tra xem có sinh viên nào không
    
    context = {"students": students, "page_title": "Xem chi tiết"}
    return render(request, "hod_templates/view_student.html", context)