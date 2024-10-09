from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from .models import *
from django.contrib import messages
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login, logout
# Create your views here.

def login_page(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Điều hướng sau khi đăng nhập thành công
            else:
                messages.error(request, "Thông tin đăng nhập không hợp lệ")
    else:
        form = LoginForm()

    return render(request, 'main_app/login.html')

def gethome(request):
    return render(request,"hod_templates/home.html")

def add_student(request):
    student_form = StudentForm(request.POST, request.FILES)
    context = {'form': student_form, "page_title": "Thêm sinh viên"}
    if request.method == "POST":
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
                    return redirect('view_student')
                except Exception as e:
                    messages.success(request, 'Lỗi 500 không thể thêm sinh viên')
                    return redirect('add_student')
        else:
            messages.success(request, 'Email đã tồn tại')
            return redirect('add_student')
    else:
        student_form = StudentForm()  # Khởi tạo form trống khi GET
        return render(request, 'hod_templates/add_student.html', context)

        # return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)
    
def add_staff(request):
    if request.method == "POST":
        staff_form = StaffForm(request.POST, request.FILES)
        if staff_form.is_valid():
            email = staff_form.cleaned_data.get("email")
            # Kiểm tra xem email đã tồn tại hay chưa
            if CustomUser.objects.filter(email=email).exists():
                messages.success(request, 'Email đã tồn tại')
                return redirect('add_staff')
            else:
                try:
                    first_name = staff_form.cleaned_data.get("first_name")
                    last_name = staff_form.cleaned_data.get("last_name")
                    gender = staff_form.cleaned_data.get("gender")
                    address = staff_form.cleaned_data.get("address")
                    password = staff_form.cleaned_data.get("password")
                    subject = staff_form.cleaned_data.get("subject")
                    passport = request.FILES.get("profile_pic")

                    # Lưu hình ảnh
                    if passport:
                        fs = FileSystemStorage()
                        filename = fs.save(passport.name, passport)
                        passport_url = fs.url(filename)
                    else:
                        passport_url = None

                    # Tạo người dùng
                    user = CustomUser.objects.create_user(
                        email=email,
                        password=password,
                        user_type=2,
                        first_name=first_name,
                        last_name=last_name,
                        profile_pic=passport_url
                    )
                    # Tạo nhân viên
                    staff = Staff(profile=user, subject=subject)
                    staff.save()

                    # Cập nhật thông tin người dùng
                    user.gender = gender
                    user.address = address
                    user.save()

                    messages.success(request, 'Thêm nhân viên thành công')
                    return redirect('view_staff')
                except Exception as e:
                    messages.error(request, f'Lỗi 500 không thể thêm sinh viên: {str(e)}')
                    return redirect('add_staff')
        else:
            # In ra lỗi cụ thể để dễ theo dõi
            messages.success(request, 'Email đã tồn tại')
            return redirect('add_staff')
    else:
        staff_form = StaffForm()  # Khởi tạo form trống khi GET
        return render(request, 'hod_templates/add_staff.html', {'form': staff_form, "page_title": "Thêm nhân viên"})

    
def add_course(request):
    form = SubjectForm(request.POST or None)
    context = {"form": form, "page_title": "Thêm khóa học"}
    if request.method == "POST":
        if form.is_valid():
            name = form.cleaned_data.get("name")
            try:
                course = Subject()
                course.name = name
                if course.name == None:
                    return redirect(reverse("add_course"), messages.success(request, "Vui lòng điền tên khóa học"))

                course.save()
                return redirect(reverse("view_subject"), messages.success(request, "Đã thêm thành công"))
            except:
                messages.error(request, "Could Not Add")
        else:
            messages.error(request, "Could Not Add")
    return render(request, "hod_templates/add_course.html", context)

def add_grade(request):
    if request.method == 'POST':
            form = GradeForm(request.POST)
            if form.is_valid():
                grade = form.save(commit=False)
                grade.teacher = request.user  # Gán giáo viên hiện tại (người đăng nhập)
                grade.save()
                return redirect('123')  # Điều hướng đến danh sách điểm sau khi lưu thành công
    return render(request, 'hod_templates/add_grade.html', {'form': GradeForm, "page_title": "Thêm điểm"})


def view_student(request):
    students = Student.objects.select_related('profile').all()  # Lấy tất cả sinh viên từ model Student
    
    if not students.exists():
        print("Không tìm thấy sinh viên nào.")  # Kiểm tra xem có sinh viên nào không
    
    context = {"students": students, "page_title": "Quản lí sinh viên"}
    return render(request, "hod_templates/view_student.html", context)

def view_staff(request):
    staffs = Staff.objects.select_related('profile').all()  # Lấy tất cả sinh viên từ model Student
    
    if not staffs.exists():
        print("Không tìm thấy sinh viên nào.")  # Kiểm tra xem có sinh viên nào không
    
    context = {"staffs": staffs, "page_title": "Quản lí nhân viên"}
    return render(request, "hod_templates/view_staff.html", context)

def view_subject(request):
    subjects = Subject.objects.all
    context = {'subjects':subjects,"page_title":"Quản lí khóa học"}
    
    return render(request, "hod_templates/view_subject.html", context)

#@login_required
def view_grade(request):
 #   if request.user.user_type == '2':  # Giáo viên
 #       grades = Grade.objects.filter(teacher=request.user)
#    elif request.user.user_type == '3':  # Sinh viên
 #       grades = Grade.objects.filter(student=request.user.student)
 #   else:
    grades = Grade.objects.all  # Admin có thể xem tất cả 
    return render(request, 'hod_templates/view_grade.html', {'grades': grades})

def edit_subject(request, subject_id):
    instance = get_object_or_404(Subject, id=subject_id)
    form = SubjectForm(request.POST or None, instance=instance)
    context = {
        "form": form,
        "subject_id": subject_id,
        "page_title": "Chỉnh sửa thông tin môn học",
    }
    
    if request.method == "POST":
        if form.is_valid():
            name = form.cleaned_data.get("name")

            try:
                subject = Subject.objects.get(id=subject_id)
                
                subject.name = name
                subject.save()
                
                
                messages.success(request, "Cập nhật thành công")
                return redirect(reverse("view_subject"))
            except Exception as e:
                messages.error(request, "Không thể cập nhật: " + str(e))       
        else:
            messages.error(request, "Điền biểu mẫu đúng cách")
    return render(request, "hod_templates/edit_subject.html", context)

def delete_subject(request, subject_id):
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        subject.delete()
        messages.success(request, "Xóa môn học thành công!")
    except Exception as e:
        messages.error(request, f"Đã xảy ra lỗi khi xóa môn học: {str(e)}")
    return redirect(reverse("view_subject"))

def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    form = StudentForm(request.POST or None, instance=student)
    context = {
        "form": form,
        "student_id": student_id,
        "page_title": "Chỉnh sửa thông tin học sinh",
    }
    if request.method == "POST":
        if form.is_valid():
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            address = form.cleaned_data.get("address")
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            gender = form.cleaned_data.get("gender")
            password = form.cleaned_data.get("password") or None
            subject = form.cleaned_data.get("subject")
            passport = request.FILES.get("profile_pic") or None
            try:
                user = CustomUser.objects.get(id=student.profile.id)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                user.gender = gender
                user.address = address
                student.subject = subject
                user.save()
                student.save()
                messages.success(request, "Cập nhật thành công")
                return redirect(reverse("view_student"))
            except Exception as e:
                messages.error(request, "Không thể cập nhật " + str(e))
        else:
            messages.error(request, "Vui lòng điền đầy đủ thông tin vào biểu mẫu!")
    else:
        return render(request, "hod_template/edit_student.html", context)