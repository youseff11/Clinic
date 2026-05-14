from django.db import migrations

def create_secretary_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='secretary')

def reverse_func(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='secretary').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0006_appointment_appointment_type_and_more'),
    ]

    operations = [
        migrations.RunPython(create_secretary_group, reverse_func),
    ]
