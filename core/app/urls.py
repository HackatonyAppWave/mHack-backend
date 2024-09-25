from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('chats/', views.get_chats, name='get_chats'),
    path('chat/<int:chat_id>', views.messages, name='messages'),
    path('addChat/', views.createChat, name='addChat'),
    path('deleteChat/', views.deleteChat, name='deleteChat'),
]
