# Generated by Django 4.1.4 on 2023-02-18 03:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0005_remove_appointment_booked_alter_appointment_add_ons_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='remarks',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
