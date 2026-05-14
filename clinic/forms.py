from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Patient, Appointment, MedicalRecord, Prescription, Doctor, Specialty ,TherapySession
from .models import Secretary
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="اسم المستخدم", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم المستخدم'}))
    password = forms.CharField(label="كلمة المرور", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'كلمة المرور'}))

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'national_id', 'gender', 'birth_date', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'name': 'الاسم الكامل',
            'national_id': 'الرقم القومي',
            'gender': 'الجنس',
            'birth_date': 'تاريخ الميلاد',
            'phone': 'رقم الهاتف',
            'address': 'العنوان',
        }

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = [
            'injury_type', 
            'total_sessions', 
            'completed_sessions', 
            'first_session_date', 
            'last_session_date', 
            'instructions'
        ]
        widgets = {
            'injury_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثلاً: انزلاق غضروفي، تأهيل رباط صليبي...'}),
            'total_sessions': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'completed_sessions': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'first_session_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'last_session_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'تعليمات التمارين المنزلية أو ملاحظات إضافية...'}),
        }
        labels = {
            'injury_type': 'نوع الإصابة / التشخيص الفيزيائي',
            'total_sessions': 'إجمالي عدد الجلسات',
            'completed_sessions': 'عدد الجلسات التي تمت',
            'first_session_date': 'تاريخ أول جلسة',
            'last_session_date': 'تاريخ آخر جلسة متوقع',
            'instructions': 'تعليمات للمريض',
        }

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'specialty', 'appointment_type', 'appointment_date', 'appointment_time', 'consultation_fee', 'status', 'notes']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'specialty': forms.Select(attrs={'class': 'form-select'}),
            'appointment_type': forms.Select(attrs={'class': 'form-select'}),
            'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'patient': 'المريض',
            'specialty': 'التخصص',
            'appointment_type': 'نوع الموعد', # الـ Label الجديد
            'appointment_date': 'تاريخ الموعد',
            'appointment_time': 'وقت الموعد',
            'consultation_fee': 'السعر المدفوع',
            'status': 'الحالة',
            'notes': 'ملاحظات',
        }
# فورم سريع لإضافة موعد مع المريض الجديد بدون اختيار المريض (لأننا هنربطهم برمجياً)
class QuickAppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['specialty', 'appointment_type', 'appointment_date', 'appointment_time', 'consultation_fee', 'status', 'notes']
        widgets = {
            'specialty': forms.Select(attrs={'class': 'form-select'}),
            'appointment_type': forms.Select(attrs={'class': 'form-select'}), # الـ Widget الجديد
            'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'specialty': 'التخصص',
            'appointment_type': 'نوع الموعد', # الـ Label الجديد
            'appointment_date': 'تاريخ الموعد',
            'appointment_time': 'وقت الموعد',
            'consultation_fee': 'السعر المدفوع',
            'status': 'الحالة',
            'notes': 'ملاحظات',
        }
class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['visit_date', 'diagnosis', 'symptoms', 'notes']
        widgets = {
            'visit_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'visit_date': 'تاريخ الزيارة',
            'diagnosis': 'التشخيص',
            'symptoms': 'الأعراض',
            'notes': 'ملاحظات الطبيب',
        }

class UserForm(forms.ModelForm):
    password = forms.CharField(label="كلمة المرور", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': 'اسم المستخدم',
            'first_name': 'الاسم الأول',
            'last_name': 'الاسم الأخير',
        }

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['specialty', 'phone']
        widgets = {
            'specialty': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'specialty': 'التخصص',
            'phone': 'رقم الهاتف',
        }
class TherapySessionForm(forms.ModelForm):
    class Meta:
        model = TherapySession
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'اكتب تطور حالة المريض والأجهزة المستخدمة في هذه الجلسة...'}),
        }
        labels = {
            'notes': 'ملاحظات الجلسة',
        }

class SecretaryForm(forms.ModelForm):
    class Meta:
        model = Secretary
        fields = ['phone']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الهاتف'}),
        }