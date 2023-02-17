# Generated by Django 4.1.4 on 2023-02-17 19:24

from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0004_alter_appointment_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='booked',
        ),
        migrations.AlterField(
            model_name='appointment',
            name='add_ons',
            field=multiselectfield.db.fields.MultiSelectField(choices=[(0, 'None'), (1, 'Tooth Brushing'), (2, 'De-matting'), (3, 'Blueberry Facial'), (4, 'Body massage'), (5, 'Hydro massage bath'), (6, 'Oatmeal or Aloe Conditioning')], default=0, max_length=11),
        ),
        migrations.AlterField(
            model_name='comment',
            name='content',
            field=models.CharField(max_length=800),
        ),
    ]