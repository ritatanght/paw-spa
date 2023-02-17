from django import forms
from .models import Pet, Appointment
from datetime import datetime, timedelta
from .utilities import check_free_time


class PetForm (forms.ModelForm):
    class Meta:
        model = Pet
        fields = ('name','size','date_of_birth','breed')
        widgets = {
            'date_of_birth': forms.DateInput(format=('%Y/%m/%d'), attrs={'type': 'date'}),
        }

    def clean(self):
        if self.cleaned_data["date_of_birth"] > datetime.today().date():
            raise forms.ValidationError("The date cannot be in the future")
        return self.cleaned_data

TIME_CHOICES = [
        (10, "10:00 AM"),
        (13, "2:00 PM"),
        (15, "3:00 PM")
    ]

class AppointmentForm (forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ('dog', 'date', 'time', 'service', 'add_ons')
        widgets = {
            'date': forms.DateInput(format=('%Y/%m/%d'), attrs={'type': 'date'}),
        }

    def clean(self):
        date = self.cleaned_data["date"]
        time = self.cleaned_data["time"]
        today = datetime.today().date()

        if date < today or (date == today and time < datetime.now().hour):
            raise  forms.ValidationError("The date or time cannot be in the past")

        elif date.weekday() == 0:
            raise  forms.ValidationError("Sorry, we are closed on Monday")
        
        elif (date - today).days/7 >= 5:
            raise  forms.ValidationError("Appointment booking is only available for dates within 5 weeks.")
        
        elif Appointment.objects.filter(date= date, time=time).exists():
            time_slot_list = list(Appointment.objects.filter(
                date=date).values_list('time', flat=True))
            all_time_slot = [10, 13, 15]
            # when the query date is today, available slot will only be the time in the future
            if date == date.today():
                for hour in all_time_slot:
                    if hour < datetime.now().hour:
                        all_time_slot.remove(hour)

            available_slot = check_free_time(all_time_slot, time_slot_list)
            if available_slot:
                raise forms.ValidationError(
                    f"Requested slot is already booked, the following time slot is still available: {', '.join(str(f'{hr}:00') for hr in available_slot)}.")
            else:
                raise forms.ValidationError(
                    "There are no available slots for the selected date.")
        return self.cleaned_data


    def __init__(self, *args, **kwargs):
        user = kwargs.pop('username', None)
        super(AppointmentForm, self).__init__(*args, **kwargs)
        self.fields['dog'].label = "Pet Name"
        self.fields['time'].label = "Time Slot"
        self.fields['add_ons'].label = "Add-on Services"
        
