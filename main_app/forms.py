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
    # subject = forms.CharField(required=True)
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
        fields = CustomUserForm.Meta.fields + ['subject', 's_code']

class StaffForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields + ['subject']
        
class SubjectForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['name']
        model = Subject

class AdminForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Admin
        fields = CustomUserForm.Meta.fields

class GradeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GradeForm, self).__init__(*args, **kwargs)
    class Meta:
        model = Grade
        fields = ['student', 'teacher', 'subject', 'exam_type', 'score',]
        
class LoginForm(forms.Form):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(label="Mật khẩu", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mật khẩu'}))

    class Meta:
        fields = ['email', 'password']

class StudentEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StudentEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields
        
