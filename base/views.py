from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib import messages as logerror
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm

# The Home View
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    query_rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q))

    topics = Topic.objects.all()
    
    room_count = query_rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))[0:5]

    context = {'rooms': query_rooms, 'topics': topics[0:5], 'topicscount' : topics.count(), 'room_count': room_count, 'room_messages':room_messages}
    return render(request, 'base/home.html', context)


def loginPage(request):
    context = {'page':'login'}
    
    if request.user.is_authenticated:
        return redirect('home')
    else:
        error = None
        if request.method == 'POST':
            email = request.POST.get('email')
            pass_word = request.POST.get('password')


            try:
                user = User.objects.get(email=email)
                
                if authenticate(request, email=email, password=pass_word):
                    login(request, user)
                    return redirect('home')
                else:
                    error = 'Incorrect username or password!'
            except:
                error = 'User does not exist!'

        return render(request, 'base/login_register.html', {'page': 'login', 'error': error})

def logoutUser(request):
    logout(request)
    return redirect('home')


def registerUser(request):
    form = MyUserCreationForm()
  
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                messages.error(request, f'{field}: {errors}')

    return render(request, 'base/login_register.html', {'form': form, 'action': 'Register'})


hostemail = [
    'jimmy@gmail.com','john.doe@gmail.com','jane.smith@gmail.com','mike.j@gmail.com','emily.white@gmail.com',  'alex.turner@gmail.com',  'grace.lee@gmail.com',    'daniel.brown@gmail.com', 'sophie.miller@gmail.com','chris.davis@gmail.com',  'olivia.wilson@gmail.com',
]

import random
# for room in programming_rooms:
#     topic, created = Topic.objects.get_or_create(name='Open Source Contributions')
#     Room.objects.create(
#                 host=User.objects.get(email=random.choice(hostemail)),
#                 topic=topic,
#                 name=room['topic'],
#                 description=room['desc'],
#             )



def room(request, pk):
    query_rooms = Room.objects.get(id=pk)
    room_messages = query_rooms.message_set.all().order_by('-created')    
    participants = query_rooms.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = query_rooms,
            body = request.POST.get('body')
        )
        query_rooms.participants.add(request.user)
        return redirect('room', pk=query_rooms.id)
    user = request.user if str(request.user) != 'AnonymousUser' else ''
    context = {'room': query_rooms, 'room_messages': room_messages, 'participants': participants, 'user':user}
    
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'topics': topics[0:5], 'topicscount': topics.count(), 'room_messages': room_messages}

    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


def updateRoom(request, pk):
    single_room = Room.objects.get(id=pk)
    form = RoomForm(instance=single_room)
    topics = Topic.objects.all()
    if request.user != single_room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        single_room.name = request.POST.get('name')
        single_room.topic = topic
        single_room.description = request.POST.get('description')
        single_room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': single_room}
    return render(request, 'base/room_form.html', context)


def deleteRoom(request, pk):
    single_room = Room.objects.get(id=pk)
    if request.method == 'POST':
        single_room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': single_room})


def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Your are not allowed')

    if request.method == 'POST':
        message.delete()
        return redirect('room')
    return render(request, 'base/delete.html', {'obj': message})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form': form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})