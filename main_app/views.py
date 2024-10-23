from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from .models import *
from django.contrib import messages
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login, logout                      

# Trang đăng nhập
def login_page(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                user = request.user
                if user.is_authenticated:
                    context = {
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                    }
                    if request.user.user_type == '1':
                        messages.success(request, 'Admin đã đăng nhập thành công')
                    else:
                        messages.success(request, f'Người dùng {user.first_name} {user.last_name} đã đăng nhập thành công')
                else:
                    context = {}
                return redirect('home')  # Chuyển hướng về trang chủ sau khi đăng nhập thành công
            else:
                messages.error(request, "Thông tin đăng nhập không hợp lệ")
    else:
        form = LoginForm()

    return render(request, 'main_app/login.html')

# Đăng xuất
def user_logout(request):
    logout(request)  # Đăng xuất người dùng
    return redirect('login')  # Chuyển hướng về trang đăng nhập

# Trang chủ với bảng xếp hạng sinh viên theo từng môn
def home_view(request):
    total_students = Student.objects.count()  # Tổng số học sinh
    total_subjects = Subject.objects.count()  # Tổng số môn học
    registers = Register.objects.all()

    passing_count = 0
    failing_count = 0
    total_students = registers.count()

    # Duyệt qua từng bản ghi của sinh viên trong từng học phần
    for register in registers:
        # Tính điểm trung bình của sinh viên
        # Kiểm tra điều kiện đậu/rớt
        if register.Average != None:
            if register.Average >= 5:
                passing_count += 1
            else:
                failing_count += 1

    # Tính tỉ lệ phần trăm đậu/rớt
    passing_rate = (passing_count / total_students) * 100 if total_students > 0 else 0
    failing_rate = (failing_count / total_students) * 100 if total_students > 0 else 0

    context = {
        'passing_rate': passing_rate,
        'failing_rate': failing_rate,
        'total_students': total_students,
        'total_subjects': total_subjects,
        'page_title': 'Trang chủ',
    }
    return render(request, 'hod_templates/home.html', context)

# Thêm khoa
def add_department(request):
    if not request.user.is_authenticated or (request.user.user_type != '1'):
        messages.error(request, 'Bạn không có quyền truy cập!!!!!')
        return redirect('home')

    form = DepartmentForm(request.POST or None, request.FILES or None)
    context = {"form": form, "page_title": "Thêm khoa"}
    
    if request.method == "POST":
        if form.is_valid():
            try:
                    # Lấy dữ liệu từ biểu mẫu
                    name = form.cleaned_data.get("name")
                    code = form.cleaned_data.get("code")
                    
                    department = Department(name=name, code=code)
                    department.save()
                    messages.success(request, 'Thêm sinh viên thành công')
                    return redirect('view_department')  # Chuyển hướng đến trang xem sinh viên

            except:
                messages.error(request, "Không thể thêm khoa")
        else:
            messages.error(request, "Biểu mẫu không hợp lệ")

    return render(request, "hod_templates/add_department.html", context)

#Xem danh sách các khoa
def view_department(request):
    if not request.user.is_authenticated or request.user.user_type != '1':
        messages.error(request, 'Bạn không có quyền truy cập!!!!!')
        return redirect('home')
    departments = Department.objects.all()
    context = {'departments': departments, "page_title": "Quản lí Khoa"}
    
    return render(request, "hod_templates/view_department.html", context)

#Chỉnh sửa thông tin khoa
def edit_department(request, department_id):
    # Kiểm tra người dùng đã đăng nhập chưa
    if not request.user.is_authenticated or request.user.user_type != '1':
        messages.error(request, 'Bạn không có quyền truy cập!!!!!')
        return redirect('home')
    # Lấy thông tin môn học cần chỉnh sửa
    instance = get_object_or_404(Department, id=department_id)
    form = DepartmentForm(request.POST or None, instance=instance)  # Khởi tạo form với dữ liệu hiện tại

    context = {
        "form": form,
        "department_id": department_id,
        "page_title": "Chỉnh sửa thông tin khoa",
    }
    
    # Xử lý khi nhận POST request
    if request.method == "POST":
        if form.is_valid():
            name = form.cleaned_data.get("name")
            code = form.cleaned_data.get("code")
            try:
                department = Department.objects.get(id=department_id)
                department.name = name
                department.code = code
                department.save()
                
                messages.success(request, "Cập nhật thành công")
                return redirect(reverse("view_subject"))
            except Exception as e:
                messages.error(request, "Không thể cập nhật: " + str(e))       
        else:
            messages.error(request, "Điền biểu mẫu đúng cách")
    
    return render(request, "hod_templates/edit_info.html", context)

#Xóa khoa
def delete_department(request, department_id):
    if not request.user.is_authenticated or request.user.user_type != '1':
        messages.error(request, 'Bạn không có quyền truy cập!!!!!')
        return redirect('home')
    try:
        department = get_object_or_404(Department, id=department_id)
        department.delete()  # Xóa môn học
        messages.success(request, "Xóa môn học thành công!")
    except Exception as e:
        messages.error(request, f"Đã xảy ra lỗi khi xóa môn học: {str(e)}")
    
    return redirect(reverse("view_department"))

#Thêm lớp học
def add_class(request):
    if not request.user.is_authenticated or (request.user.user_type != '1'):
        messages.error(request, 'Bạn không có quyền truy cập!!!!!')
        return redirect('home')

    form = ClassRoomForm(request.POST or None, request.FILES or None)
    context = {"form": form, "page_title": "Thêm lớp học"}
    
    if request.method == "POST":
        if form.is_valid():
            try:
                    # Lấy dữ liệu từ biểu mẫu
                    name = form.cleaned_data.get("name")
                    code = form.cleaned_data.get("code")
                    department = form.cleaned_data.get("department")
                    classroom = ClassRoom(name=name, code=code, department=department)
                    classroom.save()
                    messages.success(request, 'Thêm sinh viên thành công')
                    return redirect('view_class')  # Chuyển hướng đến trang xem sinh viên

            except:
                messages.error(request, "Không thể thêm khoa")
        else:
            messages.error(request, "Biểu mẫu không hợp lệ")

    return render(request, "hod_templates/add_class.html", context)

#Xem danh sách các lớp học
def view_class(request):
    if not request.user.is_authenticated :
        messages.error(request, 'Bạn không có quyền truy cập!!!!!')
        return redirect('home')
    classrooms = ClassRoom.objects.all()
    context = {'classrooms': classrooms, "page_title": "Quản lí lớp học"}
    
    return render(request, "hod_templates/view_class.html", context)

#Chỉnh sửa thông tin lớp học
def edit_class(request, classroom_id):
    # Kiểm tra người dùng đã đăng nhập chưa
    if not request.user.is_authenticated or request.user.user_type == '3':
        messages.error(request, 'Bạn không có quyền truy cập!!!!!')
        return redirect('home')
    # Lấy thông tin môn học cần chỉnh sửa
    instance = get_object_or_404(ClassRoom, id=classroom_id)
    form = ClassRoomForm(request.POST or None, instance=instance)  # Khởi tạo form với dữ liệu hiện tại

    context = {
        "form": form,
        "classroom_id": classroom_id,
        "page_title": "Chỉnh sửa thông tin lớp học",
    }
    
    # Xử lý khi nhận POST request
    if request.method == "POST":
        if form.is_valid():
            name = form.cleaned_data.get("name")
            code = form.cleaned_data.get("code")
            department = form.cleaned_data.get("department")
            try:
                classroom = ClassRoom.objects.get(id=classroom_id)
                classroom.name = name
                classroom.code = code
                classroom.department = department
                classroom.save()
                
                messages.success(request, "Cập nhật thành công")
                return redirect(reverse("view_class"))
            except Exception as e:
                messages.error(request, "Không thể cập nhật: " + str(e))       
        else:
            messages.error(request, "Điền biểu mẫu đúng cách")
    
    return render(request, "hod_templates/edit_info.html", context)

#Xóa lớp học
def delete_class(request, classroom_id):
    if not request.user.is_authenticated or request.user.user_type != '1':
        messages.error(request, 'Bạn không có quyền truy cập!!!!!')
        return redirect('home')
    try:
        classroom = get_object_or_404(ClassRoom, id=classroom_id)
        classroom.delete()  # Xóa môn học
        messages.success(request, "Xóa môn học thành công!")
    except Exception as e:
        messages.error(request, f"Đã xảy ra lỗi khi xóa môn học: {str(e)}")
    
    return redirect(reverse("view_class"))

# Thêm sinh viên
def add_student(request):
    # Kiểm tra quyền truy cập của người dùng
    if not request.user.is_authenticated or request.user.user_type != '1':
        messages.error(request, 'Bạn không có quyền truy cập!!!!!')
        return redirect('home')

    student_form = StudentForm(request.POST or None, request.FILES or None)
    context = {'form': student_form, "page_title": "Thêm sinh viên"}
    
    if request.method == "POST":
        if student_form.is_valid():
            email = student_form.cleaned_data.get("email")
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, "Email đã được đăng ký")
            else:
                try:
                    # Lấy dữ liệu từ biểu mẫu
                    first_name = student_form.cleaned_data.get("first_name")
                    last_name = student_form.cleaned_data.get("last_name")
                    code = student_form.cleaned_data.get("code")
                    gender = student_form.cleaned_data.get("gender")
                    address = student_form.cleaned_data.get("address")
                    password = student_form.cleaned_data.get("password")
                    classroom = student_form.cleaned_data.get("classroom")
                    passport = request.FILES.get("profile_pic")

                    # Xử lý ảnh đại diện
                    if passport:
                        fs = FileSystemStorage()
                        filename = fs.save(passport.name, passport)
                        passport_url = fs.url(filename)
                    else:
                        passport_url = None

                    # Tạo người dùng mới
                    user = CustomUser.objects.create_user(
                        email=email, password=password, user_type=3,
                        first_name=first_name, last_name=last_name, profile_pic=passport_url,
                    )

                    # Tạo sinh viên mới
                    student = Student(profile=user, classroom=classroom, code=code)
                    student.save()

                    # Cập nhật thông tin giới tính và địa chỉ cho người dùng
                    user.gender = gender
                    user.address = address
                    user.save()

                    messages.success(request, 'Thêm sinh viên thành công')
                    return redirect('view_student')  # Chuyển hướng đến trang xem sinh viên
                except Exception as e:
                    messages.error(request, f'Lỗi 500: Không thể thêm sinh viên. Lỗi chi tiết: {e}')
                    return redirect('add_student')
        else:
            context['form'] = student_form
            messages.error(request, f'Form không hợp lệ: {student_form.errors}')
            return render(request, 'hod_templates/add_student.html', context)
    
    return render(request, 'hod_templates/add_student.html', context)

def view_student(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Bạn không có quyền truy cập!!!!!')
        return redirect('home')

    if request.user.user_type == '1':
        students = Student.objects.all()
    else:
        students = Student.objects.filter(profile__email=request.user.email)

    context = {"students": students, "page_title": "Quản lí sinh viên"}
    return render(request, "hod_templates/view_student.html", context)

# Chỉnh sửa thông tin sinh viên
def edit_student(request, student_id):
    # Kiểm tra người dùng đã đăng nhập chưa
    if not request.user.is_authenticated:
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect('home')
    
    # Kiểm tra quyền truy cập
    if request.user.user_type != '1' and request.user.user_type != '3':  # HOD
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect(reverse("home"))
    
    student = get_object_or_404(Student, id=student_id)
    
    # Xử lý khi nhận POST request
    if request.method == 'POST':
        form = EditStudentForm(request.POST, request.FILES, instance=student.profile)  # Truyền instance là student.profile
        if form.is_valid():
            form.save()  # Lưu thông tin sinh viên
            messages.success(request, "Chỉnh sửa thông tin sinh viên thành công!")
            return redirect('view_student')  # Redirect đến danh sách sinh viên
    else:
        form = EditStudentForm(instance=student.profile)  # Khởi tạo form với thông tin hiện tại của profile
    
    return render(request, 'hod_templates/edit_info.html', {'form': form, 'student': student})

# Xóa sinh viên
def delete_student(request, student_id):
    # Kiểm tra người dùng đã đăng nhập chưa
    if not request.user.is_authenticated:
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect('home')
    
    # Kiểm tra quyền truy cập
    if request.user.user_type != '1':  # HOD
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect(reverse("home"))
    
    try:
        student = get_object_or_404(CustomUser, student__id=student_id)
        student.delete()  # Xóa sinh viên
        messages.success(request, "Xóa học sinh thành công!")
    except Exception as e:
        messages.error(request, f"Đã xảy ra lỗi khi xóa học sinh: {str(e)}")
    
    return redirect(reverse("view_student"))

# Thêm giảng viên
def add_lecturer(request):
    # Kiểm tra quyền truy cập của người dùng
    if not request.user.is_authenticated or request.user.user_type != '1':
        messages.error(request, 'Bạn không có quyền truy cập!!!!!')
        return redirect('home')

    if request.method == "POST":
        lecturer_form = LecturerForm(request.POST, request.FILES)
        if lecturer_form.is_valid():
            email = lecturer_form.cleaned_data.get("email")
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'Email đã tồn tại')
                return redirect('add_lecturer')
            else:
                try:
                    # Lấy dữ liệu từ biểu mẫu
                    first_name = lecturer_form.cleaned_data.get("first_name")
                    last_name = lecturer_form.cleaned_data.get("last_name")
                    gender = lecturer_form.cleaned_data.get("gender")
                    address = lecturer_form.cleaned_data.get("address")
                    password = lecturer_form.cleaned_data.get("password")
                    department = lecturer_form.cleaned_data.get("department")
                    study_section = lecturer_form.cleaned_data.get('study_section')

                    passport = request.FILES.get("profile_pic")

                    # Xử lý ảnh đại diện
                    if passport:
                        fs = FileSystemStorage()
                        filename = fs.save(passport.name, passport)
                        passport_url = fs.url(filename)

                    # Tạo người dùng mới
                    user = CustomUser.objects.create_user(
                        email=email, 
                        password=password, 
                        user_type=2,
                        first_name=first_name, 
                        last_name=last_name, 
                        profile_pic=passport_url
                    )
                    # Tạo nhân viên mới
                    lecturer = Lecturer(profile=user, department=department, study_section = study_section)
                    lecturer.save()

                    # Cập nhật thông tin giới tính và địa chỉ cho người dùng
                    user.gender = gender
                    user.address = address
                    user.save()

                    messages.success(request, 'Thêm nhân viên thành công')
                    return redirect('view_lecturer')  # Chuyển hướng đến trang xem nhân viên
                except Exception as e:
                    messages.error(request, f'Lỗi 500 không thể thêm nhân viên: {str(e)}')
                    return redirect('add_lecturer')
        else:
            return redirect('add_lecturer')
    else:
        lecturer_form = LecturerForm()
        return render(request, 'hod_templates/add_lecturer.html', {'form': lecturer_form, "page_title": "Thêm nhân viên"})
    
# Xem danh sách giảng viên
def view_lecturer(request):
    # Kiểm tra người dùng đã đăng nhập chưa
    if not request.user.is_authenticated:
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect('home')
     # Kiểm tra quyền truy cập
    if request.user.user_type == '1': 
        lecturer = Student.objects.all()
    elif request.user.user_type =='2':  
        lecturer = Lecturer.objects.filter(profile__email = request.user.email)
    else: 
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect(reverse("home"))
    context = {"lecturers": lecturer, "page_title": "Quản lí nhân viên"}
    return render(request, "hod_templates/view_lecturer.html", context)

# Chỉnh sửa thông tin giản viên
def edit_lecturer(request, lecturer_id):
    # Kiểm tra người dùng đã đăng nhập chưa
    if not request.user.is_authenticated:
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect('home')
    
    # Kiểm tra quyền truy cập
    if request.user.user_type != '1':  # HOD
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect(reverse("home"))
    
    lecturer = get_object_or_404(Lecturer, id=lecturer_id)
    
    # Xử lý khi nhận POST request
    if request.method == 'POST':
        form = EditLecturerForm(request.POST, request.FILES, instance=lecturer)
        if form.is_valid():
            form.save()  # Lưu thông tin nhân viên
            messages.success(request, "Chỉnh sửa thông tin nhân viên thành công!")
            return redirect('view_lecturer')  # Redirect đến danh sách nhân viên
    else:
        form = EditLecturerForm(instance=lecturer)  # Khởi tạo form với thông tin hiện tại của lecturer
    
    return render(request, 'hod_templates/edit_info.html', {'form': form, 'lecturer': lecturer})

# Xóa nhân viên
def delete_lecturer(request, lecturer_id):
    # Kiểm tra người dùng đã đăng nhập chưa
    if not request.user.is_authenticated:
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect('home')
    
    # Kiểm tra quyền truy cập
    if request.user.user_type != '1':  # HOD
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect(reverse("home"))
    
    try:
        lecturer = get_object_or_404(Lecturer, id=lecturer_id)
        lecturer.delete()  # Xóa nhân viên
        messages.success(request, "Xóa nhân viên thành công!")
    except Exception as e:
        messages.error(request, f"Đã xảy ra lỗi khi xóa nhân viên: {str(e)}")
    
    return redirect(reverse("view_lecturer"))

# Thêm môn học
def add_subject(request):
    # Kiểm tra quyền truy cập của người dùng
    if not request.user.is_authenticated or (request.user.user_type != '1' and request.user.user_type != '2'):
        messages.error(request, 'Bạn không có quyền truy cập!!!!!')
        return redirect('home')

    form = SubjectForm(request.POST or None)
    context = {"form": form, "page_title": "Thêm khóa học"}
    
    if request.method == "POST":
        if form.is_valid():
            name = form.cleaned_data.get("name")
            code = form.cleaned_data.get("code")
            credit_number = form.cleaned_data.get("credit_number")
            try:
                # Tạo môn học mới
                subject = Subject(name=name, code=code,credit_number=credit_number)
                subject.save()
                messages.success(request, "Đã thêm thành công")
                return redirect('view_subject')  # Chuyển hướng đến trang xem môn học
            except:
                messages.error(request, "Không thể thêm khóa học")
        else:
            messages.error(request, "Biểu mẫu không hợp lệ")

    return render(request, "hod_templates/add_subject.html", context)

# Xem danh sách môn học
def view_subject(request):
    # Kiểm tra người dùng đã đăng nhập chưa
    if not request.user.is_authenticated:
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect('home')
    
    # Kiểm tra quyền truy cập
    if request.user.user_type != '1' and request.user.user_type != '2':  # HOD
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect(reverse("home"))
    
    # Lấy tất cả môn học
    subjects = Subject.objects.all()
    context = {'subjects': subjects, "page_title": "Quản lí môn học"}
    
    return render(request, "hod_templates/view_subject.html", context)

# Chỉnh sửa thông tin môn học
def edit_subject(request, subject_id):
    # Kiểm tra người dùng đã đăng nhập chưa
    if not request.user.is_authenticated:
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect('home')
    
    # Kiểm tra quyền truy cập
    if request.user.user_type == '3': 
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect(reverse("home"))
    
    # Lấy thông tin môn học cần chỉnh sửa
    instance = get_object_or_404(Subject, id=subject_id)
    form = SubjectForm(request.POST or None, instance=instance)  # Khởi tạo form với dữ liệu hiện tại

    context = {
        "form": form,
        "subject_id": subject_id,
        "page_title": "Chỉnh sửa thông tin môn học",
    }
    
    # Xử lý khi nhận POST request
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

# Xóa môn học
def delete_subject(request, subject_id):
    # Kiểm tra người dùng đã đăng nhập chưa
    if not request.user.is_authenticated:
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect('home')
    
    # Kiểm tra quyền truy cập
    if request.user.user_type != '1' and request.user.user_type != '2':  # HOD
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect(reverse("home"))
    
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        subject.delete()  # Xóa môn học
        messages.success(request, "Xóa môn học thành công!")
    except Exception as e:
        messages.error(request, f"Đã xảy ra lỗi khi xóa môn học: {str(e)}")
    
    return redirect(reverse("view_subject"))

# Thêm học phần
def add_studysection(request):
    # Kiểm tra quyền truy cập của người dùng
    if not request.user.is_authenticated or (request.user.user_type != '1' and request.user.user_type != '2'):
        messages.error(request, 'Bạn không có quyền truy cập!!!!!')
        return redirect('home')

    form = StudySectionForm(request.POST or None)
    context = {"form": form, "page_title": "Thêm học phần"}
    
    if request.method == "POST":
        if form.is_valid():
            name = form.cleaned_data.get("name")
            code = form.cleaned_data.get("code")
            year = form.cleaned_data.get("year")
            subject =form.cleaned_data.get("subject")
            try:
                # Tạo môn học mới
                study_section = Study_Section(name=name, code=code,year=year,subject=subject)
                study_section.save()
                messages.success(request, "Đã thêm thành công")
                return redirect('view_studysection')  # Chuyển hướng đến trang xem môn học
            except:
                messages.error(request, "Không thể thêm học phần")
        else:
            messages.error(request, "Biểu mẫu không hợp lệ")

    return render(request, "hod_templates/add_studysection.html", context)

# Xem danh sách học phần
def view_studysection(request):
    # Kiểm tra người dùng đã đăng nhập chưa
    if not request.user.is_authenticated:
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect('home')
    
    # Lấy tất cả học phần
    studysections = Study_Section.objects.all()
    context = {'studysections': studysections, "page_title": "Quản lí học phần"}
    
    return render(request, "hod_templates/view_studysections.html", context)

# Chỉnh sửa thông tin học phần
def edit_studysection(request, studysection_id):
    # Kiểm tra người dùng đã đăng nhập chưa
    if not request.user.is_authenticated:
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect('home')
    
    # Kiểm tra quyền truy cập
    if request.user.user_type == '3': 
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect(reverse("home"))
    
    # Lấy thông tin môn học cần chỉnh sửa
    instance = get_object_or_404(Study_Section, id=studysection_id)
    form = StudySectionForm(request.POST or None, instance=instance)  # Khởi tạo form với dữ liệu hiện tại

    context = {
        "form": form,
        "studysection_id": studysection_id,
        "page_title": "Chỉnh sửa thông tin học phần",
    }
    
    # Xử lý khi nhận POST request
    if request.method == "POST":
        if form.is_valid():
            name = form.cleaned_data.get("name")
            code = form.cleaned_data.get("code")
            year = form.cleaned_data.get("year")
            subject =form.cleaned_data.get("subject")
            try:
                study_section = Study_Section.objects.get(id=studysection_id)
                study_section.name = name
                study_section.code = code
                study_section.year = year
                study_section.subject = subject
                study_section.save()
                
                messages.success(request, "Cập nhật thành công")
                return redirect(reverse("view_studysection"))
            except Exception as e:
                messages.error(request, "Không thể cập nhật: " + str(e))       
        else:
            messages.error(request, "Điền biểu mẫu đúng cách")
    
    return render(request, "hod_templates/edit_info.html", context)

# Xóa học phần
def delete_studysection(request, studysection_id):
    # Kiểm tra người dùng đã đăng nhập chưa
    if not request.user.is_authenticated:
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect('home')
    
    # Kiểm tra quyền truy cập
    if request.user.user_type != '1' and request.user.user_type != '2':  # HOD
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect(reverse("home"))
    
    try:
        studysection = get_object_or_404(Study_Section, id=studysection_id)
        studysection.delete()  # Xóa học phần
        messages.success(request, "Xóa học phần thành công!")
    except Exception as e:
        messages.error(request, f"Đã xảy ra lỗi khi xóa học phần: {str(e)}")
    
    return redirect(reverse("view_studysection"))

def register(request, student_id):
    # Lấy student instance
    student = get_object_or_404(Student, id=student_id)

    if request.user.is_authenticated and hasattr(request.user, 'student'):
        # Nếu đã đăng nhập và user là sinh viên
        student = request.user.student  
    else:
        # Nếu không, có thể báo lỗi hoặc redirect
        messages.error(request, "Bạn không có quyền truy cập.")
        return redirect('home')  # Hoặc redirect đến trang khác

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        selected_sections = request.POST.getlist('study_sections')  # Lấy danh sách học phần đã chọn
        study_sections = Study_Section.objects.filter(id__in=selected_sections, is_open=True)  # Lọc học phần đang mở

        if not study_sections.exists():  # Nếu không có học phần mở
            messages.error(request, "Hiện không có học phần nào đang mở để đăng ký.")
            return redirect('register', student_id=student.id)

        if form.is_valid():
            # Kiểm tra trùng lặp
            existing_sections = Register.objects.filter(student=student, study_section__in=study_sections)
            if existing_sections.exists():
                messages.error(request, "Bạn đã đăng ký một số học phần này.")
                return redirect('register', student_id=student.id)

            # Tạo bản ghi đăng ký mới cho sinh viên
            register = Register(student=student, semester=form.cleaned_data['semester'])
            register.save()  # Lưu đăng ký trước
            register.study_section.set(study_sections)  # Gán các học phần đã chọn
            register.save()

            # Thông báo thành công
            messages.success(request, "Đăng ký học phần thành công!")
            return redirect('view_register')
        else:
            messages.error(request, "Có lỗi trong form.")
    else:
        form = RegisterForm()

    sections = Study_Section.objects.filter(is_open=True)  # Lấy học phần đang mở
    return render(request, 'hod_templates/register.html', {'student': student, 'sections': sections, 'form': form, 'page_title': 'Đăng kí học phần'})

def view_register(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Bạn không có quyền truy cập!!!!!')
        return redirect('home')

    if request.user.user_type == '1':
        registers = Register.objects.all()
    if request.user.user_type == '2':
        registers = Register.objects.all()
    if request.user.user_type == '3':
        registers = Register.objects.filter(student__profile__email=request.user.email)

    context = {"registers": registers, "page_title": "Xem điểm"}

    return render(request, 'hod_templates/view_register.html', context)

def delete_register(request, register_id):
    if not request.user.is_authenticated:
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect('home')
    if request.user.user_type != '2':
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect(reverse("home"))
    try:
        registers = get_object_or_404(Register, id=register_id)
        registers.delete()
        messages.success(request, "Xóa học sinh thành công!")
    except Exception as e:
        messages.error(request, f"Đã xảy ra lỗi khi xóa học sinh: {str(e)}")
    return redirect(reverse("view_register"))

def add_grade(request, register_id):
    if not request.user.is_authenticated:
        messages.error(request, 'Bạn không có quyền truy cập!!!!!')
        return redirect('home')
    if request.user.user_type != '2':
        messages.error(request, 'Bạn không có quyền truy cập!!!!!')
        return redirect('home')
    user = request.user
    register = get_object_or_404(Register, id=register_id)

    try:
        lecturer = Lecturer.objects.get(profile=user)  # Lấy thông tin giáo viên
        # Kiểm tra xem giáo viên có trách nhiệm cho học phần này không
        if not register.study_section.filter(id=lecturer.study_section.id).exists():
            messages.error(request,"Bạn không có quyền thêm điểm cho sinh viên này trong học phần này.")
            return redirect('view_register')
    except Lecturer.DoesNotExist:
        messages.error(request,"Không tìm thấy thông tin giảng viên.")
        return redirect('view_register')

    # Xử lý form khi có dữ liệu POST
    if request.method == 'POST':
        form = GradeForm(request.POST, instance=register)  # Liên kết với bản ghi đã tồn tại
        if form.is_valid():
            form.save()  # Lưu lại các thay đổi
            return redirect('view_register')  # Redirect đến trang xem đăng ký
    else:
        form = GradeForm(instance=register)  # Tạo form với dữ liệu hiện tại

    return render(request, 'hod_templates/add_grade.html', {'form': form, 'register': register})
  


def edit_grade(request, register_id):
    if not request.user.is_authenticated:
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect('home')
    # Lấy instance của Grade cần sửa
    grade = get_object_or_404(Register, id=register_id)

    # Kiểm tra quyền của user, chỉ cho phép lecturer hoặc admin
    if request.user.user_type != '2':
        messages.error(request, 'Bạn không có quyền chỉnh sửa điểm!')
        return redirect('home')

    if request.method == 'POST':
        form = GradeForm(request.POST, instance=grade)  # Cập nhật với dữ liệu POST
        if form.is_valid():
            form.save()
            messages.success(request, 'Điểm đã được cập nhật thành công!')
            return redirect('view_register')
        else:
            messages.error(request, 'Dữ liệu không hợp lệ, vui lòng kiểm tra lại.')
    else:
        form = GradeForm(instance=grade)  # Khởi tạo form với dữ liệu hiện tại của Grade

    return render(request, 'hod_templates/edit_info.html', {'form': form, 'page_title': 'Chỉnh sửa điểm'})

def delete_grade(request, register_id):
    if not request.user.is_authenticated:
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect('home')
    if request.user.user_type != '2':
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect(reverse("home"))
    try:
        grade = get_object_or_404(Register, id=register_id)
        grade.homework_score.delete()
        grade.midterm_score.delete()
        grade.final_score.delete()
        messages.success(request, "Xóa học sinh thành công!")
    except Exception as e:
        messages.error(request, f"Đã xảy ra lỗi khi xóa học sinh: {str(e)}")
    return redirect(reverse("view_register"))

def search_view(request):
    if not request.user.is_authenticated:
        messages.error(request,'Bạn không có quyền truy cập!!!!!')
        return redirect('home')
    query = request.GET.get('q', '').strip()  # Lấy từ khóa tìm kiếm từ GET request và loại bỏ khoảng trắng ở đầu và cuối

    # Tách các từ trong từ khóa tìm kiếm
    query_terms = query.split()

    # Tìm kiếm sinh viên theo họ và tên
    students = Student.objects.filter(
        Q(profile__first_name__icontains=query_terms[0]) | Q(profile__last_name__icontains=query_terms[0])
    )
    for term in query_terms[1:]:
        students = students | Student.objects.filter(
            Q(profile__first_name__icontains=term) | Q(profile__last_name__icontains=term)
        )

    # Tìm kiếm giáo viên theo họ và tên
    teachers = Lecturer.objects.filter(
        Q(profile__first_name__icontains=query_terms[0]) | Q(profile__last_name__icontains=query_terms[0])
    )
    for term in query_terms[1:]:
        teachers = teachers | Lecturer.objects.filter(
            Q(profile__first_name__icontains=term) | Q(profile__last_name__icontains=term)
        )

    context = {
        'query': query,
        'students': students,
        'teachers': teachers,
    }
    return render(request, 'hod_templates/search_results.html', context)

