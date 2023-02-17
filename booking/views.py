import json
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.db import IntegrityError
from datetime import datetime, timedelta

from .models import User, Owner, Pet, Appointment, Comment
from .forms import PetForm, AppointmentForm
from .utilities import load_preview_dict


# Create your views here.
def index(request):
    # Only show comments that are approved by staff and get 10 of them randomly (if there are more than 10)
    comments = Comment.objects.filter(
        approved=True).order_by('?')[:10]

    # Add new comment
    if request.method == "POST":
        data = json.loads(request.body)
        comment = data["comment"]
        username = data["username"]
        user = User.objects.get(username=username)

        if user is None:
            return JsonResponse({
                "message": "Login Required"
            }, status=403)

        Comment.objects.create(user=user, content=comment)
        return JsonResponse({
            "message": "Thank you for your comment!"
        }, status=200)

    else:
        return render(request, 'booking/index.html', {"comments": comments})


def services(request):
    return render(request, 'booking/services.html')


def login_view(request):
    if request.method == "POST":
        next = request.POST['next']
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            if next == "":
                return HttpResponseRedirect(reverse('profile'))
            else:
                return HttpResponseRedirect(next)
                  
        else:
            return render(request, "booking/login.html", {
                'next': next,
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, 'booking/login.html')


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        phone = request.POST["phone"]
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "booking/register.html", {
                "message": "Passwords do not match."
            })

        if phone and (len(phone) != 10 or not phone.isnumeric()):
            return render(request, "booking/register.html", {
                "message": "Phone number invalid. Must be 10 digits and in format: 9051234567"
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            Owner.objects.create(user=user, phone=phone)

        except IntegrityError:
            return render(request, "booking/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, 'booking/register.html')


@login_required(login_url='/login')
def profile(request):
    today = datetime.today()

    owner = Owner.objects.get(user=request.user)
    pets = Pet.objects.filter(owner=owner)
    # only show upcoming bookings
    booking = Appointment.objects.filter(user=owner, date__gte=today).exclude(
        date=today, time__lt=today.now().hour).order_by('date', 'time')

    if request.method == "POST":
        form = PetForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            size = form.cleaned_data["size"]
            date_of_birth = form.cleaned_data["date_of_birth"]
            breed = form.cleaned_data["breed"].title()
            Pet.objects.create(owner=owner, name=name, size=size,
                               date_of_birth=date_of_birth, breed=breed)
            return HttpResponseRedirect(reverse("profile"))
        else:
            return render(request, "booking/profile.html", {
                "form": form,
                "owner": owner,
                "pets": pets,
                "booking": booking,
                "today": datetime.today()
            })

    elif request.method == "DELETE":
        data = json.loads(request.body)
        pet_id = data["pet"]
        # including owner in the query adds a layer to verification
        pet = Pet.objects.filter(owner=owner, id=pet_id)
        pet.delete()
        return HttpResponse(status=204)

    elif request.method == 'PUT':
        data = json.loads(request.body)
        field = data['field']
        value = data['value']
        if field == 'phone':
            if len(value) == 10 and value.isnumeric():
                owner.phone = value
                owner.save()
            else:
                return JsonResponse({"message": "Phone number should have 10 digits and numbers only."}, status=400)
        elif field == 'email':
            if '@' in value:
                user = User.objects.get(username=request.user)
                user.email = value
                user.save()
                return HttpResponse(status=204)
            else:
                return JsonResponse({"message": "Please input an valid email"}, status=400)

    else:
        return render(request, "booking/profile.html", {
            "petform": PetForm(),
            "owner": owner,
            "pets": pets,
            "booking": booking,
            "today": today,
            "bookform": AppointmentForm(),
        })


@login_required(login_url='/login')
def booking(request):
    # preview slot table
    today = datetime.today().date()
    date_list = [today + timedelta(days=x) for x in range(7)]
    appointments = Appointment.objects.filter(
        date__range=[date_list[0], date_list[-1]])

    slot_dict = {}
    for date in date_list:
        if date.weekday() == 0:
            slot_dict[date] = 'Closed'
        else:
            time_list = [10, 13, 15]
            time_slot_list = list(Appointment.objects.filter(
                date=date).values_list('time', flat=True))

            for i in range(len(time_list)):
                if time_list[i] in time_slot_list or (date == today and datetime.now().hour > time_list[i]):
                    time_list[i] = 'x'

            slot_dict[date] = time_list

    # users should only be able to choose the pets they own
    bookform = AppointmentForm()
    owner = Owner.objects.get(user__username=request.user)
    bookform.fields["dog"].queryset = Pet.objects.filter(owner=owner)

    if request.method == "POST":
        owner = Owner.objects.get(user=request.user)
        # the booking form
        if request.POST.get("book"):
            bookform = AppointmentForm(request.POST)

            if bookform.is_valid():
                date = bookform.cleaned_data["date"]
                time = bookform.cleaned_data["time"]
                available = Appointment.objects.filter(date=date, time=time)
                if available.count() == 0:
                    dog = bookform.cleaned_data["dog"]
                    service = bookform.cleaned_data["service"]
                    add_ons = bookform.cleaned_data["add_ons"]
                    Appointment.objects.create(
                        user=owner, dog=dog, date=date, time=time, service=service, add_ons=add_ons, booked=True)
                    return HttpResponseRedirect(reverse('profile'))

            else:  # booking form invalid
                return render(request, 'booking/booking.html', {
                    "form": bookform,
                    "petform": PetForm(),
                    "date_list": slot_dict,
                })

        # the add pet form
        elif request.POST.get('add_pet'):
            petform = PetForm(request.POST)
            if petform.is_valid():
                name = petform.cleaned_data["name"]
                size = petform.cleaned_data["size"]
                date_of_birth = petform.cleaned_data["date_of_birth"]
                breed = petform.cleaned_data["breed"].title()
                Pet.objects.create(owner=owner, name=name, size=size,
                                   date_of_birth=date_of_birth, breed=breed)
                message = f"{name} is added successfully"
                return render(request, 'booking/booking.html', {
                    "form": bookform,
                    "petform": PetForm(),
                    "date_list": slot_dict,
                    "message": message
                })
            # pet form invalid
            else:
                return render(request, "booking/booking.html", {
                    "form": bookform,
                    "petform": petform,
                    "date_list": slot_dict,
                })

    else:  # Get method
        return render(request, 'booking/booking.html', {
            "form": bookform,
            "petform": PetForm(),
            "date_list": slot_dict
        })


@login_required(login_url='/login')
def appointment(request, id):
    try:
        appointment = Appointment.objects.get(pk=id)
    except Appointment.DoesNotExist:
        return JsonResponse({"error": "Record not found."}, status=404)

    owner = Owner.objects.get(user=request.user)
    if owner.id == appointment.user.id:
        # cancel appointment
        if request.method == "DELETE":
            if owner.id == appointment.user.id:
                data = json.loads(request.body)
                id = data["id"]
                appointment.delete()
                return HttpResponse(status=204)
            else:
                return JsonResponse({'error': 'You can only delete your own appointments'}, status=403)

        # edit appointment
        elif request.method == 'PUT':
            data = json.loads(request.body)
            date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            time = data["time"]
            dog = data["dog"]

            if date < datetime.today().date() or (date == datetime.today().date() and time < str(datetime.now().hour)):
                return JsonResponse({'error': 'Cannot change to a time slot in the past'}, status=400)
            elif date.weekday() == 0:
                return JsonResponse({'error': 'Sorry, we are closed on Monday'}, status=400)

            # in case customer is not changing the date and time fields
            available = Appointment.objects.filter(
                date=date, time=time).exclude(id=id)
            if available.count() == 0:
                appointment.dog = Pet.objects.get(pk=dog)
                appointment.service = data["service"]
                appointment.add_ons = data["add_ons"]
                appointment.date = date
                appointment.time = time
                appointment.save()
                return HttpResponse(status=200)

            else:
                return JsonResponse({'error': 'Time slot taken'}, status=400)

        # GET method
        else:
            return JsonResponse(appointment.serialize())

    else:
        return JsonResponse({'error': 'This is not your appointment'}, status=403)


@login_required(login_url='/login')
def schedule(request, start, move):

    today = datetime.today().date()
    if move == 'next':
        # preview and booking for within 5 weeks only
        if (start + timedelta(days=7) - today).days/7 >= 5:
            return JsonResponse({"message": "Preview and booking are only available for dates within 5 weeks."}, status=400)
        else:
            start = start + timedelta(days=7)
            slot_dict = load_preview_dict(start)
            return JsonResponse({"slot_dict": slot_dict}, status=200)
    elif move == 'prev':
        if start <= today:
            return JsonResponse({"message": "Cannot view slot in the past"}, status=400)
        else:
            start = start - timedelta(days=7)
            slot_dict = load_preview_dict(start)
            return JsonResponse({"slot_dict": slot_dict}, status=200)
    else:
        return JsonResponse({"message": "Invalid request"}, status=400)
