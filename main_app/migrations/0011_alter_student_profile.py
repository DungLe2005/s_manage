# Generated by Django 3.2.4 on 2024-10-08 08:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0010_alter_student_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='profile',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='main_app.customuser'),
        ),
    ]