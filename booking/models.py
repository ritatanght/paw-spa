from django.contrib.auth.models import User
from django.db import models
from multiselectfield import MultiSelectField


# Create your models here.
class Owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10, null=True, blank=True)

class Pet(models.Model):
    SIZE_CHOICES = [
        ("S", "Small (Up to 30 lbs)"),
        ("M", "Medium (30 - 50 lbs)"),
        ("L", "Large (50 lbs and Up)")
    ]
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name="owner")
    name = models.CharField(max_length=50)
    size = models.CharField(
        max_length=20, choices=SIZE_CHOICES, default="")
    date_of_birth = models.DateField(null=True, blank=True)
    breed = models.CharField(max_length=50)

    def __str__(self):
        return self.name
 


class Appointment(models.Model):
    SERVICE_CHOICES = [
        ("E", "Express Grooming"),
        ("F", "Full Dog Grooming"),
        ("P", "Spa Premium Grooming")
    ]

    ADDONS_CHOICES = [
        (0, "None"),
        (1, "Tooth Brushing"),
        (2, "De-matting"),
        (3, "Blueberry Facial"),
        (4, "Body massage"),
        (5, "Hydro massage bath"),
        (6, "Oatmeal or Aloe Conditioning"),
    ]

    TIME_CHOICES = [
        (10, "10:00 AM"),
        (13, "1:00 PM"),
        (15, "3:00 PM")
    ]

    user = models.ForeignKey(
        Owner, on_delete=models.CASCADE)
    dog = models.ForeignKey(
        Pet, on_delete=models.CASCADE, default="")
    date = models.DateField(default="", null=False) 
    time = models.IntegerField(choices=TIME_CHOICES, )
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES, default="E")
    add_ons = MultiSelectField(
        choices=ADDONS_CHOICES, max_choices=6, max_length=11, default=0)
    booked = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('date', 'time')

    def __str__(self):
        return f"Ref#{self.id:05d} -{self.get_time_display()} on {self.date} for {self.dog}"

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.id,
            "dog": self.dog.name,
            "date": self.date.strftime("%b %#d %Y (%a)"),
            "time": self.get_time_display(),
            "service": self.get_service_display(),
            "add_ons": self.get_add_ons_display(),
            "add_ons_list": self.add_ons,
            "created": self.created.strftime("%b %#d %Y, %I:%M %p")
        }
    

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=800)
    approved = models.BooleanField(default=False)

    def __str__(self):
        if self.approved:
            return f'Approved - "{self.content}"'
        else:
            return f'Pending Approval - "{self.content}"'
