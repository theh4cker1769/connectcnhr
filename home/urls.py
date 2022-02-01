from unicodedata import name
from django.contrib import admin
from django.urls import path, include
from home import views

urlpatterns = [
    path('', views.index, name='index'),
    path('room/<int:pk>', views.room, name='room'),
    path('profile/<int:pk>', views.userProfile, name='userProfile'),
    
    path('create-room', views.create_room, name='create_room'),
    path('update-room/<str:pk>', views.update_room, name='update_room'),
    path('delete-room/<str:pk>', views.delete_room, name='delete_room'),
    path('delete-message/<str:pk>', views.delete_message, name='delete_message'),

    path('update-user', views.update_user, name='update_user'),
    path('topics', views.topics, name='topics'),
    path('activity', views.activity, name='activity'),

    path('login', views.login_user, name='login_user'),
    path('register', views.register_user, name='register_user'),
    path('logout', views.logout_user, name='logout_user'),
]
