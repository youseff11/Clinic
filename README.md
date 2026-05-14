# 🏛️ نظام إدارة عيادة جامعة القاهرة

## تشغيل المشروع

```bash
# 1. تثبيت Django
pip install django

# 2. تطبيق قاعدة البيانات
python manage.py migrate

# 3. تشغيل السيرفر
python manage.py runserver
```
ثم افتح المتصفح على: http://127.0.0.1:8000

---

## بيانات الدخول الافتراضية

| الدور | اسم المستخدم | كلمة المرور |
|-------|------------|------------|
| مسؤول (Admin) | admin | admin123 |
| طبيب | doctor1 | doctor123 |

---

## مميزات النظام

### شاشة الإدارة (للمسؤول)
- لوحة إحصائيات شاملة (المرضى، الأطباء، المواعيد)
- إضافة وتعديل وعرض بيانات المرضى مع رقم تسلسلي
- إدارة المواعيد (بالتاريخ والوقت والتخصص والدكتور)
- عرض جميع الأطباء والسجلات الطبية

### شاشة الطبيب
- مواعيد اليوم مع بيانات المريض الكاملة
- ملف المريض: بياناته + سجله الطبي + مواعيده
- إضافة سجل طبي (تشخيص، أعراض، ملاحظات)
- إضافة روشتة بالأدوية والجرعات والمدة
- تحديث حالة الموعد

### بنية المشروع
```
clinic_project/
├── clinic/           # التطبيق الوحيد
│   ├── models.py    # نماذج البيانات
│   ├── views.py     # المنطق
│   ├── forms.py     # النماذج
│   └── urls.py      # الروابط
├── templates/        # قالب واحد
│   ├── base.html
│   ├── login.html
│   ├── admin/       # قوالب الإدارة
│   └── doctor/      # قوالب الطبيب
└── manage.py
```

## إضافة طبيب جديد
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> from clinic.models import Doctor, Specialty
>>> u = User.objects.create_user('doctor2', password='pass123', first_name='محمد', last_name='علي')
>>> Doctor.objects.create(user=u, specialty=Specialty.objects.get(name='جراحة'))
```
