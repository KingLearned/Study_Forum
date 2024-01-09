from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    query_rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q))

    topics = Topic.objects.all()[0:5]
    room_count = query_rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))[0:5]

    context = {'rooms': query_rooms, 'topics': topics, 'room_count': room_count, 'room_messages':room_messages}
    return render(request, 'base/home.html', context)


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            email = request.POST.get('email')
            pass_word = request.POST.get('password')

            try:
                user = User.objects.get(email == email)
            except:
                messages.error(request, 'User does not exist!')

            user = authenticate(request, email=email, password=pass_word)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Username or Password does not exist!')

        context = {'page':page}
        return render(request, 'base/login_register.html', context)


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
            messages.error(request, 'Any Occurred!')
            
    return render(request, 'base/login_register.html', {'form': form})


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
    context = {'room': query_rooms, 'room_messages': room_messages, 'participants': participants}
    
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'topics': topics, 'room_messages': room_messages}

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