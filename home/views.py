import imp
from multiprocessing import context
from pydoc_data.topics import topics
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm

# Create your views here.

# rooms = [
#     {'id':1,'name':'My First ID123'},
#     {'id':2,'name':'My Second ID'},
#     {'id':3,'name':'My Third ID'},
# ]

def login_user(request):
    page = 'login_user'
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exists')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')

    context = {'page': page}
    return render(request, 'login_register.html', context)


def logout_user(request):
    logout(request)
    return redirect('/')


def register_user(request):
    form = MyUserCreationForm()

    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'An error occurred')
        
    context = {'form':form}
    return render(request, 'login_register.html', context)


def index(request):

    # q = request.GET.get('q') if request.GET.get('q') != None else ''

    if request.GET.get('q') != None:
        q = request.GET.get('q')
    else:
        q = ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains = q) |
        Q(name__icontains = q) |
        Q(description__icontains = q) 
    )
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))[0:4]

    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'index.html', context)


def room(request, pk):
    # room = None
    # for i in rooms:
    #     if i['id'] == int(pk):
    #         room = i
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.filter(parent=None)
    room_reply = room.message_set.filter(parent__isnull=False)
    participants = room.participants.all()

    if request.method == 'POST':
        messageId = request.POST.get('messageId')
        if messageId == "":
            message = Message.objects.create(
                user = request.user,
                room=room,
                body=request.POST.get('body')
            )
            room.participants.add(request.user)
        else:
            message = Message.objects.create(
                user = request.user,
                room=room,
                body=request.POST.get('body'),
                parent=Message.objects.get(id=messageId)
            )
            room.participants.add(request.user)

        return redirect('room', pk=room.id)    

    context = {'room': room, 'room_messages':room_messages, 'room_reply':room_reply, 'participants': participants}
    return render(request, 'room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'profile.html', context)


@login_required(login_url='login_user')
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
        )
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
        return redirect('/')
    context = {'form': form, 'topics': topics}
    return render(request, 'create_room.html', context)


@login_required(login_url='login_user')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('How dare you !!!!!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        # form = RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()
        return redirect('/')
            
    context = {'form':form, 'topics': topics, 'room': room}
    return render(request, 'create_room.html', context)


@login_required(login_url='login_user')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    topicidtes = room.topic.name
    notopics = Room.objects.filter(topic__name=topicidtes)

    if request.user != room.host:
        return HttpResponse('How dare you !!!!!!')

    if request.method == 'POST':
        if notopics.count() == 1:
            room.topic.delete()
        room.delete()
        return redirect('/')
            
    return render(request, 'delete.html', {'obj':room, 'notopics':notopics})


@login_required(login_url='login_user')
def delete_message(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('How dare you !!!!!!')

    if request.method == 'POST':
        message.delete()
        return redirect('/')
            
    return render(request, 'delete.html', {'obj':message})


@login_required(login_url='login_user')
def update_user(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('userProfile', pk=user.id)

    context = {'form':form}
    return render(request, 'update-user.html', context)


def topics(request):

    if request.GET.get('q') != None:
        q = request.GET.get('q')
    else:
        q = ''

    topics = Topic.objects.filter(name__icontains = q)

    context = {'topics': topics}
    return render(request, 'topics.html', context)


def activity(request):
    room_messages = Message.objects.all()

    context = {'room_messages': room_messages}
    return render(request, 'activity.html', context)
