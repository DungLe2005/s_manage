# Generated by Django 4.2.14 on 2024-10-19 09:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0006_lecturer_grade'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lecturer',
            name='grade',
        ),
    ]