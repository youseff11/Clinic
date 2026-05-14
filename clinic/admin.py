from django.contrib import admin
# تم إضافة TherapySession هنا
from .models import Specialty, Doctor, Patient, Appointment, MedicalRecord, Prescription, Secretary, TherapySession

# تخصيص عنوان لوحة التحكم الأساسية
admin.site.site_header = 'إدارة عيادة جامعة القاهرة'
admin.site.site_title = 'عيادة جامعة القاهرة'
admin.site.index_title = 'لوحة تحكم الإدارة'

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'specialty', 'phone')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone')
    list_filter = ('specialty',)

    def get_full_name(self, obj):
        return f"د. {obj.user.get_full_name() or obj.user.username}"
    get_full_name.short_description = 'اسم الطبيب'

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('patient_number', 'name', 'national_id', 'gender', 'phone', 'created_at')
    search_fields = ('name', 'national_id', 'phone')
    list_filter = ('gender', 'created_at')
    ordering = ('-created_at',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    # التعديلات هنا: ضفنا نوع الموعد ومين اللي سجله
    list_display = ('patient', 'appointment_type', 'doctor', 'appointment_date', 'appointment_time', 'status', 'created_by')
    list_filter = ('status', 'appointment_type', 'appointment_date', 'specialty', 'doctor', 'created_by')
    search_fields = ('patient__name', 'patient__national_id', 'doctor__user__username')
    date_hierarchy = 'appointment_date'
    ordering = ('-appointment_date', '-appointment_time')

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'visit_date')
    list_filter = ('visit_date', 'doctor')
    search_fields = ('patient__name', 'patient__national_id', 'diagnosis')
    date_hierarchy = 'visit_date'
    ordering = ('-visit_date',)

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('injury_type', 'patient_name', 'doctor', 'total_sessions', 'completed_sessions', 'first_session_date', 'created_at')
    search_fields = ('injury_type', 'medical_record__patient__name')
    list_filter = ('created_at', 'doctor')

    def patient_name(self, obj):
        return obj.medical_record.patient.name
    patient_name.short_description = 'اسم المريض'

# =========================================
# =========== إضافة الجلسات العلاجية =======
# =========================================
@admin.register(TherapySession)
class TherapySessionAdmin(admin.ModelAdmin):
    list_display = ('get_patient_name', 'doctor', 'session_date')
    list_filter = ('session_date', 'doctor')
    search_fields = ('prescription__medical_record__patient__name',)
    date_hierarchy = 'session_date'
    
    def get_patient_name(self, obj):
        return obj.prescription.medical_record.patient.name
    get_patient_name.short_description = 'اسم المريض'

# =========================================
# =========== إضافة السكرتارية ============
# =========================================
@admin.register(Secretary)
class SecretaryAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'phone')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone')

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'اسم السكرتير/ة'