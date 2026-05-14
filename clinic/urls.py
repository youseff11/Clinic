from django.urls import path
from . import views

urlpatterns = [
    # ==========================================
    # ===== AUTHENTICATION (تسجيل الدخول) =====
    # ==========================================
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ==========================================
    # ======== ADMIN PANEL (لوحة الإدارة) =======
    # ==========================================
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    
    # إدارة المرضى (Patients Management)
    path('admin-panel/patients/', views.admin_patients, name='admin_patients'),
    path('admin-panel/patients/add/', views.admin_patient_add, name='admin_patient_add'),
    path('admin-panel/patients/<int:pk>/', views.admin_patient_detail, name='admin_patient_detail'),
    path('admin-panel/patients/<int:pk>/edit/', views.admin_patient_edit, name='admin_patient_edit'),
    path('admin-panel/patients/send-sms/', views.send_bulk_sms, name='send_bulk_sms'),
    
    # إدارة المواعيد (Appointments Management)
    path('admin-panel/appointments/', views.admin_appointments, name='admin_appointments'),
    path('admin-panel/appointments/add/', views.admin_appointment_add, name='admin_appointment_add'),
    path('appointment/<int:pk>/print/', views.print_slip, name='print_slip'),
    
    # إدارة الأطباء (Doctors Management)
    path('admin-panel/doctors/', views.admin_doctors, name='admin_doctors'),
    path('admin-panel/doctors/add/', views.admin_doctor_add, name='admin_doctor_add'),
    path('admin-panel/doctors/<int:pk>/', views.admin_doctor_detail, name='admin_doctor_detail'),
    
    # السجلات الطبية (Medical Records)
    path('admin-panel/records/', views.admin_records, name='admin_records'),

    path('admin-panel/secretaries/', views.admin_secretaries, name='admin_secretaries'),
    path('admin-panel/secretaries/add/', views.admin_secretary_add, name='admin_secretary_add'),

    # ==========================================
    # ======= DOCTOR PANEL (لوحة الطبيب) =======
    # ==========================================
    path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    
    # المواعيد والمرضى
    path('appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('appointment/<int:appt_pk>/handle/', views.doctor_handle_appointment, name='doctor_handle_appointment'),
    path('appointment/<int:pk>/update-status/', views.update_appointment_status, name='update_appointment_status'),
    path('my-sessions/', views.doctor_sessions_history, name='doctor_sessions_history'),
    path('patient/<int:pk>/', views.doctor_patient_detail, name='doctor_patient_detail'),
    
    # العمليات الطبية (Records, Prescriptions, Sessions)
    path('patient/<int:patient_pk>/add-record/', views.doctor_add_record, name='doctor_add_record'),
    path('record/<int:record_pk>/add-prescription/', views.doctor_add_prescription, name='doctor_add_prescription'),
    path('prescription/<int:prescription_pk>/add-session/', views.add_therapy_session, name='add_therapy_session'),

    # ==========================================
    # =========== AJAX & UTILITIES =============
    # ==========================================
    path('admin-panel/patients/search-ajax/', views.search_patients_ajax, name='search_patients_ajax'),
    path('ajax/load-doctors/', views.load_doctors, name='ajax_load_doctors'),
    path('ajax/check-patient-record/', views.check_patient_record_ajax, name='check_patient_record_ajax'),

    # ==========================================
    # ====== SECRETARY PANEL (السكرتيرة) =======
    # ==========================================
    path('secretary/', views.secretary_dashboard, name='secretary_dashboard'),
    path('secretary/patients/', views.secretary_patients, name='secretary_patients'),
    path('secretary/patients/add/', views.secretary_patient_add, name='secretary_patient_add'),
    path('secretary/patients/<int:pk>/', views.secretary_patient_detail, name='secretary_patient_detail'),
    path('secretary/appointments/', views.secretary_appointments, name='secretary_appointments'),
    path('secretary/appointments/add/', views.secretary_appointment_add, name='secretary_appointment_add'),
    path('secretary/appointment/<int:pk>/update-status/', views.secretary_appointment_update_status, name='secretary_appointment_update_status'),
    path('secretary/appointment/<int:pk>/print/', views.secretary_print_slip, name='secretary_print_slip'),
    path('secretary/patients/search-ajax/', views.secretary_search_patients_ajax, name='secretary_search_patients_ajax'),
    path('secretary/doctors/', views.secretary_doctors, name='secretary_doctors'),
]
