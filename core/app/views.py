from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from rest_framework.decorators import api_view
import json

from .mAsystent.mAsystent import mAsystent
from .mAsystent.memory import create_memory

# Create your views here.
def home(request):
    return HttpResponse("Hello")


@api_view(['GET'])
def get_chats(request):
    if not Chat.objects.exists():
        Chat.objects.create()

    chats = Chat.objects.all().order_by("-created")

    if request.GET.get("id", None) is None:
        if not chats.first().is_empty:
            Chat.objects.create()

    chats = Chat.objects.all().order_by("-created")
    chats_serializer = ChatSerializer(chats, many=True)

    return Response(chats_serializer.data, status=status.HTTP_200_OK)
    

@api_view(['GET', 'POST'])
def messages(request, chat_id):
    chat = Chat.objects.filter(id=chat_id)
    if not chat.exists():
        return Response({}, status=status.HTTP_404_NOT_FOUND)
    chat = chat.first()

    if request.method == "GET":
        data = MessageSerializer(Message.objects.filter(chat = chat).all().order_by('created'), many=True).data
        return Response(data)
    
    elif request.method == "POST":
        data = request.data
        message_content = data.get('message')
        Message.objects.create(
            chat=chat,
            content = message_content,
            ai_response = False
        )

        messages = MessageSerializer(Message.objects.all().order_by('-created'), many=True).data
        messages = [dict(m) for m in messages]
        memory = create_memory(messages)
        resp = mAsystent(memory)(message_content)

        ai_message = Message.objects.create(
            chat=chat,
            content = resp["output"],
            ai_response = True
        )
        serialized_message = MessageSerializer(ai_message)
        data = {
            **serialized_message.data,
            **resp
        }
        
        return Response(data)


@api_view(['POST'])
def createChat(request):
    if request.method == "POST":
        chat_instance = Chat() 
        chat_instance.save()

        serializer = ChatSerializer(chat_instance)
        
        return Response(serializer.data)
    return Response({'message': 'Chat not created'}, status=400)

@api_view(['POST','GET'])
def deleteChat(request):
    if request.method == "POST":
        data = json.loads(request.body)

        chat_id_rcv = data.get('chat_id')
        
        if chat_id_rcv:
            Chat.objects.filter(id = chat_id_rcv).delete()
        
        return Response({'message': 'Chat deleted'})
    return Response({'message': 'Chat not deleted'}, status=400)