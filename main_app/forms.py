from django import forms

from .models import *


class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        # Thay đổi giao diện của các trường
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'
            
class CustomUserForm(FormSettings):
    first_name = forms.CharField(required=True, label="Họ")
    last_name = forms.CharField(required=True, label="tên")
    email = forms.EmailField(required=True, label="Email")
    gender = forms.ChoiceField(choices=[('M', 'Nam'), ('F', 'Nữ')], label="Giới tính")
    address = forms.CharField(widget=forms.Textarea, label="Địa chỉ")
    password = forms.CharField(widget=forms.PasswordInput, label="Mật khẩu")
    widget = {
        'password': forms.PasswordInput(),
    }
    profile_pic = forms.ImageField(label="Hình ảnh đại diện")

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)

        if kwargs.get('instance'):
            instance = kwargs.get('instance').admin.__dict__
            self.fields['password'].required = False
            for field in CustomUserForm.Meta.fields:
                self.fields[field].initial = instance.get(field)
            if self.instance.pk is not None:
                self.fields['password'].widget.attrs['placeholder'] = "Điền vào đây nếu bạn muốn cập nhật mật khẩu"

    def clean_email(self, *args, **kwargs):
        formEmail = self.cleaned_data['email'].lower()
        if self.instance.pk is None:  # Thêm mới
            if CustomUser.objects.filter(email=formEmail).exists():
                raise forms.ValidationError("Email đã được đăng ký")
        else:  # Cập nhật
            dbEmail = self.Meta.model.objects.get(
                id=self.instance.pk).admin.email.lower()
            if dbEmail != formEmail:  # Có sự thay đổi
                if CustomUser.objects.filter(email=formEmail).exists():
                    raise forms.ValidationError("Email đã được đăng ký")

        return formEmail
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name','email', 'gender', 'password', 'profile_pic', 'address']
        
class StudentForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields + ['birth_day', 'code', 'classroom']
    birth_day = forms.DateTimeField( required=True, label='Ngày sinh')
    code =  forms.CharField(required=True, label="Mã số sinh viên")
    classroom = forms.ModelChoiceField(queryset=ClassRoom.objects.all(), required=True, label="Lớp")  # Trường chọn Lớp

class DepartmentForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(DepartmentForm, self).__init__(*args, **kwargs)

    name = forms.CharField(required=True, label="Tên Khoa")
    code = forms.CharField(required=True, label="Mã khoa")
    class Meta:
        model = Department
        fields = ['name', 'code']

class LecturerForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(LecturerForm, self).__init__(*args, **kwargs)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=True, label="Khoa")  # Trường chọn Khoa
    study_section = forms.ModelChoiceField(queryset=Study_Section.objects.all(), required=True, label="Mon")  # Trường chọn Khoa
    class Meta(CustomUserForm.Meta):
        model = Lecturer
        fields = CustomUserForm.Meta.fields + ['department', 'study_section']
        
class SubjectForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['name','code','credit_number']
        model = Subject
    name = forms.CharField(required=True, label="Tên môn học")
    code = forms.CharField(required=True, label="Mã môn học")
    credit_number = forms.IntegerField( required=True, label="Số tính chỉ")

class StudySectionForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(StudySectionForm, self).__init__(*args, **kwargs)
    class Meta:
        fields = ['name','code','year','subject']
        model = Subject
    name = forms.CharField(required=True, label="Tên học phần")
    code = forms.CharField(required=True, label="Mã học phần")
    year = forms.IntegerField(required=True, label="Năm học")
    subject= forms.ModelChoiceField(queryset=Subject.objects.all(), required=True, label="Thuộc môn học")  # Trường chọn môn học

class RegisterForm(forms.ModelForm):
    study_sections = forms.ModelMultipleChoiceField(
        queryset=Study_Section.objects.filter(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),  # Thêm class cho checkbox
        required=True,
        label="Chọn học phần"
    )
    
    class Meta:
        model = Register
        fields = ['study_sections', 'semester']

    
        
class ClassRoomForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(ClassRoomForm, self).__init__(*args, **kwargs)
    class Meta:
        model = ClassRoom
        fields = ['name', 'code', 'department']
    name = forms.CharField(required=True, label="Tên lớp học")
    code = forms.CharField(required=True, label="Mã lớp học")
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=True, label="Thuộc khoa")
        
class LoginForm(forms.Form):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(label="Mật khẩu", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mật khẩu'}))

    class Meta:
        fields = ['email', 'password']

class EditStudentForm(forms.ModelForm):
    birth_day = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'], 
        required=True
    )    
    code =  forms.CharField(required=True, label="Mã số sinh viên")
    classroom = forms.ModelChoiceField(queryset=ClassRoom.objects.all(), required=True, label="Lớp")  # Trường chọn Lớp
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'gender', 'password', 'address', 'profile_pic', 'email', 'birth_day', 'code', 'classroom']  # Các field mà bạn muốn chỉnh sửa

    def save(self, commit=True):
        user = super(EditStudentForm, self).save(commit=False)
        
        current_email = self.instance.email  # Lấy email hiện tại
        if current_email != user.email:
            if CustomUser.objects.filter(email=user.email).exists():
                raise forms.ValidationError("Email đã tồn tại. Vui lòng sử dụng email khác.")
        
        if commit:
            user.save()
        return user

class EditLecturerForm(forms.ModelForm):
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=True, label="Khoa")
    study_section = forms.ModelChoiceField(queryset=Study_Section.objects.all(), required=True, label="Mon")  # Trường chọn Khoa

    class Meta:
        model = Lecturer
        fields =['department','study_section']  # Các field mà bạn muốn chỉnh sửa

    
class GradeForm(FormSettings):
    class Meta:
        model = Register
        fields = ['midterm_score', 'final_score', 'homework_score']
        widgets = {
            'midterm_score': forms.NumberInput(attrs={'min': 0, 'max': 10, 'step': 0.01}),
            'final_score': forms.NumberInput(attrs={'min': 0, 'max': 10, 'step': 0.01}),
            'homework_score': forms.NumberInput(attrs={'min': 0, 'max': 10, 'step': 0.01}),
        }