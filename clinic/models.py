from django.db import models
from django.contrib.auth.models import User


class Specialty(models.Model):
    name = models.CharField(max_length=100, verbose_name="التخصص")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "تخصص"
        verbose_name_plural = "التخصصات"


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True, verbose_name="التخصص")
    phone = models.CharField(max_length=20, blank=True, verbose_name="رقم الهاتف")

    def __str__(self):
        return f"د. {self.user.get_full_name() or self.user.username}"

    class Meta:
        verbose_name = "دكتور"
        verbose_name_plural = "الأطباء"


class Patient(models.Model):
    GENDER_CHOICES = [('M', 'ذكر'), ('F', 'أنثى')]
    patient_number = models.AutoField(primary_key=True, verbose_name="رقم المريض")
    name = models.CharField(max_length=150, verbose_name="الاسم")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="الجنس")
    birth_date = models.DateField(verbose_name="تاريخ الميلاد")
    phone = models.CharField(max_length=20, blank=True, verbose_name="رقم الهاتف")
    address = models.TextField(blank=True, verbose_name="العنوان")
    created_at = models.DateTimeField(auto_now_add=True)
    national_id = models.CharField(max_length=14, unique=True, verbose_name="الرقم القومي", null=True, blank=True)

    def __str__(self):
        if self.national_id:
            return f"#{self.patient_number} - {self.name} - {self.national_id}"
        return f"#{self.patient_number} - {self.name}"

    class Meta:
        verbose_name = "مريض"
        verbose_name_plural = "المرضى"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('confirmed', 'مؤكد'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي'),
    ]
    
    # === التعديل الجديد: خيارات نوع الموعد ===
    TYPE_CHOICES = [
        ('new', 'كشف جديد'),
        ('followup', 'استشارة / متابعة'),
        ('session', 'جلسة علاجية'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments', verbose_name="المريض")
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments', verbose_name="الدكتور")
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, verbose_name="التخصص")
    
    # === الحقل الجديد ===
    appointment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='new', verbose_name="نوع الموعد")
    
    appointment_date = models.DateField(verbose_name="تاريخ الموعد")
    appointment_time = models.TimeField(verbose_name="وقت الموعد")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="الحالة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="السعر المدفوع", default=0.0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_appointments', verbose_name="تم التسجيل بواسطة")

    def __str__(self):
        return f"{self.patient.name} - {self.get_appointment_type_display()} - {self.appointment_date}"

    class Meta:
        verbose_name = "موعد"
        verbose_name_plural = "المواعيد"
        ordering = ['appointment_date', 'appointment_time']


class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records', verbose_name="المريض")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name="الدكتور")
    appointment = models.OneToOneField(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='medical_record', verbose_name="الموعد")
    visit_date = models.DateField(verbose_name="تاريخ الزيارة")
    diagnosis = models.TextField(verbose_name="التشخيص")
    symptoms = models.TextField(blank=True, verbose_name="الأعراض")
    notes = models.TextField(blank=True, verbose_name="ملاحظات الطبيب")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.name} - {self.visit_date}"

    class Meta:
        verbose_name = "سجل طبي"
        verbose_name_plural = "السجلات الطبية"
        ordering = ['-visit_date']


class Prescription(models.Model):
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='prescriptions', verbose_name="السجل الطبي")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name="الدكتور")
    
    # حقول خطة العلاج الطبيعي الجديدة
    injury_type = models.CharField(max_length=200, verbose_name="نوع الإصابة")
    total_sessions = models.PositiveIntegerField(verbose_name="إجمالي عدد الجلسات", default=1)
    completed_sessions = models.PositiveIntegerField(verbose_name="عدد الجلسات المنفذة", default=0)
    first_session_date = models.DateField(verbose_name="تاريخ أول جلسة", null=True, blank=True)
    last_session_date = models.DateField(verbose_name="تاريخ آخر جلسة", null=True, blank=True)
    
    instructions = models.TextField(blank=True, verbose_name="تعليمات إضافية")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def remaining_sessions(self):
        return max(0, self.total_sessions - self.completed_sessions)

    def __str__(self):
        return f"{self.injury_type} - {self.medical_record.patient.name}"

    class Meta:
        verbose_name = "خطة جلسات"
        verbose_name_plural = "خطط الجلسات"
        
class TherapySession(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='sessions', verbose_name="خطة الجلسات")
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, verbose_name="الطبيب المعالج")
    session_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ ووقت الجلسة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات الجلسة وتطور الحالة")

    class Meta:
        verbose_name = "جلسة علاجية"
        verbose_name_plural = "الجلسات العلاجية"
        ordering = ['-session_date'] # عشان أحدث جلسة تظهر فوق

    def __str__(self):
        return f"جلسة يوم {self.session_date.strftime('%Y-%m-%d')} - {self.prescription.medical_record.patient.name}"

class Secretary(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    phone = models.CharField(max_length=20, blank=True, verbose_name="رقم الهاتف")

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    class Meta:
        verbose_name = "سكرتير/ة"
        verbose_name_plural = "طاقم السكرتارية"