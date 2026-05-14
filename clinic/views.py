# ==========================================
# ================ IMPORTS =================
# ==========================================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q, F
from django.utils import timezone
from datetime import date
from django.http import JsonResponse
from django.urls import reverse
from .models import Patient, Appointment, MedicalRecord, Prescription, Doctor, Specialty, TherapySession
from .forms import LoginForm, PatientForm, AppointmentForm, QuickAppointmentForm, MedicalRecordForm, PrescriptionForm, UserForm, DoctorForm, TherapySessionForm
from django.contrib.auth.models import Group
from .models import Secretary  # ضيف Secretary للموديلات اللي بتستوردها
from .forms import SecretaryForm
from django.db.models import Count, Q
from django.utils.timezone import now
# ==========================================
# ========== AUTHENTICATION VIEWS ==========
# ==========================================
def is_admin(user):
    return user.is_superuser or user.is_staff

def is_secretary(user):
    return user.groups.filter(name='secretary').exists()

def login_view(request):
    if request.user.is_authenticated:
        if is_admin(request.user):
            return redirect('admin_dashboard')
        if is_secretary(request.user):
            return redirect('secretary_dashboard')
        return redirect('doctor_dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if is_admin(user):
                return redirect('admin_dashboard')
            if is_secretary(user):
                return redirect('secretary_dashboard')
            return redirect('doctor_dashboard')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')


# ==========================================
# ============== ADMIN VIEWS ===============
# ==========================================
@login_required
@user_passes_test(is_admin, login_url='login')
def admin_dashboard(request):
    today = date.today()
    stats = {
        'total_patients': Patient.objects.count(),
        'total_doctors': Doctor.objects.count(),
        'today_appointments': Appointment.objects.filter(appointment_date=today).count(),
        'total_appointments': Appointment.objects.count(),
        'pending': Appointment.objects.filter(status='pending').count(),
        'completed': Appointment.objects.filter(status='completed').count(),
    }
    today_appointments = Appointment.objects.filter(appointment_date=today).select_related('patient', 'doctor', 'specialty').order_by('appointment_time')
    recent_patients = Patient.objects.order_by('-created_at')[:5]
    return render(request, 'admin/dashboard.html', {'stats': stats, 'today_appointments': today_appointments, 'recent_patients': recent_patients})

@login_required
@user_passes_test(is_admin, login_url='login')
def admin_patients(request):
    query = request.GET.get('q', '')
    patients = Patient.objects.all()
    if query:
        patients = patients.filter(Q(name__icontains=query) | Q(phone__icontains=query) | Q(national_id__icontains=query))
    patients = patients.order_by('-created_at')
    return render(request, 'admin/patients.html', {'patients': patients, 'query': query})

@login_required
@user_passes_test(is_admin, login_url='login')
def admin_patient_add(request):
    if request.method == 'POST':
        p_form = PatientForm(request.POST)
        a_form = QuickAppointmentForm(request.POST)
        if p_form.is_valid() and a_form.is_valid():
            patient = p_form.save()
            appointment = a_form.save(commit=False)
            appointment.patient = patient
            appointment.save()
            messages.success(request, f'تم إضافة المريض {patient.name} وحجز الموعد بنجاح - رقمه: {patient.patient_number}')
            return redirect('admin_patients')
    else:
        p_form = PatientForm()
        a_form = QuickAppointmentForm()
    return render(request, 'admin/patient_form.html', {'p_form': p_form, 'a_form': a_form, 'title': 'إضافة مريض وحجز موعد'})

@login_required
@user_passes_test(is_admin, login_url='login')
def admin_patient_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث بيانات المريض بنجاح')
            return redirect('admin_patients')
    else:
        form = PatientForm(instance=patient)
    return render(request, 'admin/patient_form.html', {'p_form': form, 'title': 'تعديل بيانات المريض', 'patient': patient})

@login_required
@user_passes_test(is_admin, login_url='login')
def admin_patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    appointments = patient.appointments.select_related('doctor', 'specialty').order_by('-appointment_date')
    records = patient.medical_records.select_related('doctor').prefetch_related('prescriptions').order_by('-visit_date')
    return render(request, 'admin/patient_detail.html', {'patient': patient, 'appointments': appointments, 'records': records})

@login_required
@user_passes_test(is_admin, login_url='login')
def admin_appointments(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    appointments = Appointment.objects.select_related('patient', 'doctor', 'specialty')
    if query:
        appointments = appointments.filter(Q(patient__name__icontains=query) | Q(doctor__user__first_name__icontains=query))
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    appointments = appointments.order_by('-appointment_date', '-appointment_time')
    return render(request, 'admin/appointments.html', {'appointments': appointments, 'query': query, 'status_filter': status_filter})

@login_required
@user_passes_test(is_admin, login_url='login')
def admin_appointment_add(request):
    patient_id = request.GET.get('patient')
    initial_data = {}
    patient_obj = None
    
    if patient_id:
        initial_data['patient'] = patient_id
        patient_obj = get_object_or_404(Patient, pk=patient_id)

    active_prescriptions = []
    if patient_obj:
        active_prescriptions = list(Prescription.objects.filter(
            medical_record__patient=patient_obj,
        ).filter(completed_sessions__lt=F('total_sessions')).select_related('medical_record').order_by('-created_at'))

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة الموعد بنجاح')
            if patient_id:
                return redirect('admin_patient_detail', pk=patient_id)
            return redirect('admin_appointments')
    else:
        form = AppointmentForm(initial=initial_data)
        
    return render(request, 'admin/appointment_form.html', {
        'form': form, 
        'title': 'إضافة موعد جديد',
        'patient_obj': patient_obj,
        'active_prescriptions': active_prescriptions,
    })

@login_required
@user_passes_test(is_admin, login_url='login')
def admin_doctors(request):
    doctors = Doctor.objects.select_related('user', 'specialty').annotate(appt_count=Count('appointments'))
    return render(request, 'admin/doctors.html', {'doctors': doctors})

@login_required
@user_passes_test(is_admin, login_url='login')
def admin_doctor_add(request):
    if request.method == 'POST':
        u_form = UserForm(request.POST)
        d_form = DoctorForm(request.POST)
        if u_form.is_valid() and d_form.is_valid():
            user = u_form.save(commit=False)
            user.set_password(u_form.cleaned_data['password'])
            user.save()
            doctor = d_form.save(commit=False)
            doctor.user = user
            doctor.save()
            messages.success(request, 'تم إضافة الطبيب بنجاح')
            return redirect('admin_doctors')
    else:
        u_form = UserForm()
        d_form = DoctorForm()
    return render(request, 'admin/doctor_form.html', {'u_form': u_form, 'd_form': d_form, 'title': 'إضافة طبيب جديد'})

@login_required
@user_passes_test(is_admin, login_url='login')
def admin_doctor_detail(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    appointments = doctor.appointments.all().order_by('-appointment_date')
    prescriptions = Prescription.objects.filter(doctor=doctor).order_by('-created_at')
    return render(request, 'admin/doctor_detail.html', {'doctor': doctor, 'appointments': appointments, 'prescriptions': prescriptions})

@login_required
@user_passes_test(is_admin, login_url='login')
def admin_records(request):
    records = MedicalRecord.objects.select_related('patient', 'doctor').prefetch_related('prescriptions').order_by('-visit_date')
    return render(request, 'admin/records.html', {'records': records})

@login_required
@user_passes_test(is_admin, login_url='login')
def send_bulk_sms(request):
    if request.method == 'POST':
        message_text = request.POST.get('sms_message')
        patients_with_phones = Patient.objects.exclude(phone__isnull=True).exclude(phone__exact='')
        count = 0
        for patient in patients_with_phones:
            phone = patient.phone
            count += 1
        messages.success(request, f'تم إرسال الرسالة بنجاح لـ {count} مريض!')
        return redirect('admin_patients')
    return redirect('admin_patients')

@login_required
@user_passes_test(is_admin, login_url='login')
def admin_secretaries(request):
    today = now().date()
    
    # التعديل هنا: جبنا بيانات السكرتارية وعملنا حقل إضافي بيعد مواعيد النهاردة
    secretaries = Secretary.objects.select_related('user').annotate(
        today_cases=Count(
            'user__created_appointments',
            filter=Q(user__created_appointments__created_at__date=today)
        )
    )
    return render(request, 'admin/secretaries.html', {'secretaries': secretaries})

@login_required
@user_passes_test(is_admin, login_url='login')
def admin_secretary_add(request):
    if request.method == 'POST':
        u_form = UserForm(request.POST)
        s_form = SecretaryForm(request.POST)
        if u_form.is_valid() and s_form.is_valid():
            # إنشاء المستخدم
            user = u_form.save(commit=False)
            user.set_password(u_form.cleaned_data['password'])
            user.save()
            
            # إضافة المستخدم لجروب السكرتارية تلقائياً
            group, created = Group.objects.get_or_create(name='secretary')
            user.groups.add(group)
            
            # إنشاء بروفايل السكرتير
            secretary = s_form.save(commit=False)
            secretary.user = user
            secretary.save()
            
            messages.success(request, 'تم إضافة السكرتير/ة بنجاح')
            return redirect('admin_secretaries')
    else:
        u_form = UserForm()
        s_form = SecretaryForm()
        
    return render(request, 'admin/secretary_form.html', {
        'u_form': u_form, 
        's_form': s_form, 
        'title': 'إضافة سكرتير/ة جديد'
    })


# ==========================================
# ============== DOCTOR VIEWS ==============
# ==========================================
@login_required
def doctor_dashboard(request):
    if is_admin(request.user):
        return redirect('admin_dashboard')
    try:
        doctor = request.user.doctor
    except Doctor.DoesNotExist:
        messages.error(request, 'حسابك غير مرتبط بطبيب. تواصل مع الإدارة.')
        return redirect('login')
    
    today = date.today()
    
    today_appointments = Appointment.objects.filter(
        specialty=doctor.specialty,
        appointment_date=today
    ).select_related('patient', 'specialty', 'doctor').order_by('appointment_time')
    
    upcoming = Appointment.objects.filter(
        specialty=doctor.specialty,
        appointment_date__gt=today,
        status__in=['pending', 'confirmed']
    ).select_related('patient', 'specialty', 'doctor').order_by('appointment_date', 'appointment_time')[:5]
    
    stats = {
        'today_count': today_appointments.count(),
        'total_department_patients': Appointment.objects.filter(specialty=doctor.specialty).values('patient').distinct().count(),
        'pending_today': today_appointments.filter(status='pending').count(),
        'completed_today': today_appointments.filter(status='completed').count(),
    }
    
    return render(request, 'doctor/dashboard.html', {
        'doctor': doctor, 
        'today_appointments': today_appointments, 
        'upcoming': upcoming, 
        'stats': stats
    })

@login_required
def doctor_patient_detail(request, pk):
    if is_admin(request.user):
        return redirect('admin_patient_detail', pk=pk)
    try:
        doctor = request.user.doctor
    except Doctor.DoesNotExist:
        return redirect('login')
        
    patient = get_object_or_404(Patient, pk=pk)
    records = patient.medical_records.filter(appointment__specialty=doctor.specialty).prefetch_related('prescriptions').order_by('-visit_date')
    all_appointments = patient.appointments.filter(specialty=doctor.specialty).order_by('-appointment_date')
    
    return render(request, 'doctor/patient_detail.html', {'patient': patient, 'records': records, 'appointments': all_appointments, 'doctor': doctor})

@login_required
def doctor_add_record(request, patient_pk):
    if is_admin(request.user):
        return redirect('admin_dashboard')
    try:
        doctor = request.user.doctor
    except Doctor.DoesNotExist:
        return redirect('login')
        
    patient = get_object_or_404(Patient, pk=patient_pk)
    appointment_id = request.GET.get('appointment')
    appointment = None
    
    if appointment_id:
        appointment = get_object_or_404(Appointment, pk=appointment_id, specialty=doctor.specialty)
        
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.patient = patient
            record.doctor = doctor
            
            if appointment:
                record.appointment = appointment
                appointment.status = 'completed'
                appointment.doctor = doctor
                appointment.save()
                
            record.save()
            messages.success(request, 'تم إضافة السجل الطبي بنجاح')
            return redirect('doctor_patient_detail', pk=patient.pk)
    else:
        form = MedicalRecordForm(initial={'visit_date': date.today()})
        
    return render(request, 'doctor/add_record.html', {'form': form, 'patient': patient, 'appointment': appointment})

@login_required
def doctor_add_prescription(request, record_pk):
    if is_admin(request.user):
        return redirect('admin_dashboard')
    try:
        doctor = request.user.doctor
    except Doctor.DoesNotExist:
        return redirect('login')
        
    record = get_object_or_404(MedicalRecord, pk=record_pk, appointment__specialty=doctor.specialty)
    
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.medical_record = record
            prescription.doctor = doctor
            prescription.save()
            messages.success(request, 'تم إضافة خطة الجلسات بنجاح')
            return redirect('doctor_patient_detail', pk=record.patient.pk)
    else:
        form = PrescriptionForm(initial={
            'injury_type': record.diagnosis,
            'first_session_date': date.today()
        })
        
    return render(request, 'doctor/add_prescription.html', {'form': form, 'record': record})

@login_required
def doctor_appointments(request):
    if is_admin(request.user):
        return redirect('admin_appointments')
    try:
        doctor = request.user.doctor
    except Doctor.DoesNotExist:
        return redirect('login')
        
    appointments = Appointment.objects.filter(specialty=doctor.specialty).select_related('patient', 'specialty', 'doctor').order_by('-appointment_date', 'appointment_time')
    return render(request, 'doctor/appointments.html', {'appointments': appointments, 'doctor': doctor})

@login_required
def doctor_handle_appointment(request, appt_pk):
    appointment = get_object_or_404(Appointment, pk=appt_pk)
    patient = appointment.patient
    if request.user.is_superuser or request.user.is_staff:
        return redirect('admin_dashboard')
    
    try:
        doctor = request.user.doctor
    except AttributeError:
        messages.error(request, 'حسابك غير مرتبط بطبيب.')
        return redirect('login')

    if not appointment.doctor:
        appointment.doctor = doctor
        appointment.save()

    if appointment.appointment_type == 'session':
        active_prescription = Prescription.objects.filter(
            medical_record__patient=patient,
            medical_record__appointment__specialty=appointment.specialty,
        ).filter(
            completed_sessions__lt=F('total_sessions')
        ).order_by('-created_at').first()

        if active_prescription:
            url = reverse('add_therapy_session', kwargs={'prescription_pk': active_prescription.pk})
            return redirect(f"{url}?appointment={appt_pk}")
        else:
            messages.warning(request, 'لم يتم العثور على خطة جلسات نشطة لهذا المريض. يمكنك إضافة خطة جديدة من ملف المريض.')
            return redirect('doctor_patient_detail', pk=patient.pk)
    else:
        url = reverse('doctor_add_record', kwargs={'patient_pk': patient.pk})
        return redirect(f"{url}?appointment={appt_pk}")

@login_required
def add_therapy_session(request, prescription_pk):
    prescription = get_object_or_404(Prescription, pk=prescription_pk)
    appointment_id = request.GET.get('appointment')
    
    if prescription.completed_sessions >= prescription.total_sessions:
        messages.warning(request, "تم اكتمال جميع الجلسات المحددة لهذه الخطة!")
        return redirect('doctor_patient_detail', pk=prescription.medical_record.patient.pk)

    if request.method == 'POST':
        form = TherapySessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.prescription = prescription            
            if hasattr(request.user, 'doctor'):
                session.doctor = request.user.doctor
            session.save()
            prescription.completed_sessions += 1            
            if prescription.completed_sessions == 1 and not prescription.first_session_date:
                prescription.first_session_date = timezone.now().date()
            if prescription.completed_sessions == prescription.total_sessions:
                prescription.last_session_date = timezone.now().date()
            prescription.save()
            if appointment_id:
                Appointment.objects.filter(pk=appointment_id).update(status='completed')
            messages.success(request, 'تم تسجيل الجلسة وتحديث حالة الموعد بنجاح!')            
            return redirect('doctor_dashboard')
    else:
        form = TherapySessionForm()
        
    return render(request, 'doctor/add_session.html', {
        'form': form, 
        'prescription': prescription,
        'appointment_id': appointment_id
    })

@login_required
def doctor_sessions_history(request):
    if is_admin(request.user):
        return redirect('admin_dashboard')
    
    try:
        doctor = request.user.doctor
    except Doctor.DoesNotExist:
        messages.error(request, 'حسابك غير مرتبط بطبيب.')
        return redirect('login')

    sessions = TherapySession.objects.filter(doctor=doctor).select_related(
        'prescription__medical_record__patient',
        'prescription'
    ).order_by('-session_date')

    return render(request, 'doctor/sessions_history.html', {
        'sessions': sessions,
        'doctor': doctor
    })

@login_required
def update_appointment_status(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['pending', 'confirmed', 'completed', 'cancelled']:
            appointment.status = new_status
            appointment.save()
            messages.success(request, 'تم تحديث حالة الموعد')
    return redirect(request.META.get('HTTP_REFERER', 'doctor_dashboard'))


# ==========================================
# =============== AJAX VIEWS ===============
# ==========================================
@login_required
@user_passes_test(is_admin, login_url='login')
def search_patients_ajax(request):
    query = request.GET.get('q', '')
    if query:
        patients = Patient.objects.filter(
            Q(name__icontains=query) | 
            Q(phone__icontains=query) | 
            Q(national_id__icontains=query)
        )[:10]
    else:
        # لو مفيش بحث، هات أحدث 10 مرضى
        patients = Patient.objects.all().order_by('-created_at')[:10]
        
    results = []
    for p in patients:
        results.append({
            'id': p.pk,
            'number': p.patient_number,
            'name': p.name,
            'national_id': p.national_id if p.national_id else '-',
            'phone': p.phone if p.phone else '-'
        })
    return JsonResponse({'patients': results})

@login_required
def check_patient_record_ajax(request):
    patient_id = request.GET.get('patient_id')
    specialty_id = request.GET.get('specialty_id')
    
    if patient_id and specialty_id:
        has_record = MedicalRecord.objects.filter(
            patient_id=patient_id, 
            appointment__specialty_id=specialty_id
        ).exists()
        return JsonResponse({'has_record': has_record})
        
    return JsonResponse({'has_record': False})

@login_required
def load_doctors(request):
    specialty_id = request.GET.get('specialty_id')
    if specialty_id:
        doctors = Doctor.objects.filter(specialty_id=specialty_id).select_related('user')
    else:
        doctors = Doctor.objects.all().select_related('user')
    
    doctor_list = []
    for doctor in doctors:
        name = doctor.user.get_full_name() or doctor.user.username
        doctor_list.append({'id': doctor.id, 'name': f"د. {name}"})
        
    return JsonResponse(doctor_list, safe=False)
@login_required
@user_passes_test(is_admin, login_url='login')
def print_slip(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    return render(request, 'admin/print_slip.html', {'appointment': appointment})

# ==========================================
# =========== SECRETARY VIEWS ==============
# ==========================================
@login_required
@user_passes_test(is_secretary, login_url='login')
def secretary_dashboard(request):
    today = date.today()
    stats = {
        'total_patients': Patient.objects.count(),
        'today_appointments': Appointment.objects.filter(appointment_date=today).count(),
        'pending': Appointment.objects.filter(status='pending').count(),
        'confirmed': Appointment.objects.filter(status='confirmed').count(),
    }
    today_appointments = Appointment.objects.filter(appointment_date=today).select_related('patient', 'doctor', 'specialty').order_by('appointment_time')
    recent_patients = Patient.objects.order_by('-created_at')[:5]
    return render(request, 'secretary/dashboard.html', {
        'stats': stats,
        'today_appointments': today_appointments,
        'recent_patients': recent_patients,
    })

@login_required
@user_passes_test(is_secretary, login_url='login')
def secretary_patients(request):
    query = request.GET.get('q', '')
    patients = Patient.objects.all()
    if query:
        patients = patients.filter(Q(name__icontains=query) | Q(phone__icontains=query) | Q(national_id__icontains=query))
    patients = patients.order_by('-created_at')
    return render(request, 'secretary/patients.html', {'patients': patients, 'query': query})

@login_required
@user_passes_test(is_secretary, login_url='login')
def secretary_patient_add(request):
    if request.method == 'POST':
        p_form = PatientForm(request.POST)
        a_form = QuickAppointmentForm(request.POST)
        if p_form.is_valid() and a_form.is_valid():
            patient = p_form.save()
            
            # التعديل هنا: ربط الموعد بالسكرتيرة اللي بتسجل
            appointment = a_form.save(commit=False)
            appointment.patient = patient
            appointment.created_by = request.user  # <--- السطر السحري
            appointment.save()
            
            messages.success(request, f'تم إضافة المريض {patient.name} وحجز الموعد بنجاح - رقمه: {patient.patient_number}')
            return redirect('secretary_patients')
    else:
        p_form = PatientForm()
        a_form = QuickAppointmentForm()
    return render(request, 'secretary/patient_form.html', {'p_form': p_form, 'a_form': a_form, 'title': 'إضافة مريض وحجز موعد'})

@login_required
@user_passes_test(is_secretary, login_url='login')
def secretary_patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    appointments = patient.appointments.select_related('doctor', 'specialty').order_by('-appointment_date')
    return render(request, 'secretary/patient_detail.html', {'patient': patient, 'appointments': appointments})

@login_required
@user_passes_test(is_secretary, login_url='login')
def secretary_appointments(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    appointments = Appointment.objects.select_related('patient', 'doctor', 'specialty')
    if query:
        appointments = appointments.filter(Q(patient__name__icontains=query) | Q(doctor__user__first_name__icontains=query))
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    appointments = appointments.order_by('-appointment_date', '-appointment_time')
    return render(request, 'secretary/appointments.html', {'appointments': appointments, 'query': query, 'status_filter': status_filter})

@login_required
@user_passes_test(is_secretary, login_url='login')
def secretary_appointment_add(request):
    patient_id = request.GET.get('patient')
    initial_data = {}
    patient_obj = None
    if patient_id:
        initial_data['patient'] = patient_id
        patient_obj = get_object_or_404(Patient, pk=patient_id)
        
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            # التعديل هنا: ربط الموعد بالسكرتيرة اللي بتسجل
            appointment = form.save(commit=False)
            appointment.created_by = request.user  # <--- السطر السحري
            appointment.save()
            
            messages.success(request, 'تم إضافة الموعد بنجاح')
            if patient_id:
                return redirect('secretary_patient_detail', pk=patient_id)
            return redirect('secretary_appointments')
    else:
        form = AppointmentForm(initial=initial_data)
    return render(request, 'secretary/appointment_form.html', {
        'form': form,
        'title': 'إضافة موعد جديد',
        'patient_obj': patient_obj,
    })

@login_required
@user_passes_test(is_secretary, login_url='login')
def secretary_appointment_update_status(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['pending', 'confirmed', 'completed', 'cancelled']:
            appointment.status = new_status
            appointment.save()
            messages.success(request, 'تم تحديث حالة الموعد')
    return redirect(request.META.get('HTTP_REFERER', 'secretary_appointments'))

@login_required
@user_passes_test(is_secretary, login_url='login')
def secretary_search_patients_ajax(request):
    query = request.GET.get('q', '')
    if query:
        patients = Patient.objects.filter(
            Q(name__icontains=query) | Q(phone__icontains=query) | Q(national_id__icontains=query)
        )[:10]
    else:
        # لو مفيش بحث، هات أحدث 10 مرضى
        patients = Patient.objects.all().order_by('-created_at')[:10]
        
    results = [{'id': p.pk, 'number': p.patient_number, 'name': p.name,
                'national_id': p.national_id if p.national_id else '-',
                'phone': p.phone if p.phone else '-'} for p in patients]
    return JsonResponse({'patients': results})

@login_required
@user_passes_test(is_secretary, login_url='login')
def secretary_print_slip(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    return render(request, 'admin/print_slip.html', {'appointment': appointment})

@login_required
@user_passes_test(is_secretary, login_url='login')
def secretary_doctors(request):
    # بنجيب كل الدكاترة مع تخصصاتهم وبنعد مواعيدهم للعرض فقط
    doctors = Doctor.objects.select_related('user', 'specialty').annotate(appt_count=Count('appointments'))
    return render(request, 'secretary/doctors.html', {'doctors': doctors})