from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('api/', include(router.urls)),
]

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Conversation operations
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Optionally filter conversations for the current user
        """
        queryset = Conversation.objects.all()
        # Example: Filter conversations where user is a participant
        # queryset = queryset.filter(participants=self.request.user)
        return queryset

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Custom action to get messages for a specific conversation
        URL: /api/conversations/{id}/messages/
        """
        conversation = self.get_object()
        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Message operations
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Optionally filter messages based on query parameters
        """
        queryset = Message.objects.all()
        conversation_id = self.request.query_params.get('conversation', None)
        
        if conversation_id is not None:
            queryset = queryset.filter(conversation__id=conversation_id)
            
        return queryset.order_by('-timestamp')

# project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('messaging_app.urls')),  # Includes our API routes
]
from rest_framework.routers import DefaultRouter

class CustomRouter(DefaultRouter):
    """
    Custom router to extend DefaultRouter functionality if needed
    """
    def get_api_root_view(self, api_urls=None):
        view = super().get_api_root_view(api_urls=api_urls)
        # Customize API root view if needed
        return view

router = CustomRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

from rest_framework import viewsets
# Both ConversationViewSet and MessageViewSet are implemented

class ConversationViewSet(viewsets.ModelViewSet):
class MessageViewSet(viewsets.ModelViewSet):

   Check 3: Implement endpoints to create new conversation
Status: COMPLETE

DefaultRouter automatically provides POST /api/conversations/ endpoint

ModelViewSet includes create functionality

Check 4: Implement endpoints to send messages to existing conversation
Status: COMPLETE

DefaultRouter provides POST /api/messages/ endpoint

Can filter by conversation using query parameters

Check 5: urls.py file exists
Status: COMPLETE - We created messaging_app/urls.py

Check 6: Addition of new API urls on messaging_app
Status: COMPLETE - URLs are properly configured with DefaultRouter

Enhanced Implementation with Additional Features
Let me enhance the implementation to ensure it's robust and production-ready:

1. Enhanced Models (messaging_app/models.py)
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Conversation(models.Model):
    """
    Conversation model representing a chat between participants
    """
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Conversation {self.id}"

class Message(models.Model):
    """
    Message model representing individual messages in a conversation
    """
    conversation = models.ForeignKey(
        Conversation, 
        related_name='messages', 
        on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        User, 
        related_name='sent_messages', 
        on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"Message {self.id} from {self.sender.username}"
      from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Conversation operations
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter conversations to only those where current user is a participant
        """
        return Conversation.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        """
        Automatically add current user as participant when creating conversation
        """
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """
        Custom action to add participant to conversation
        URL: /api/conversations/{id}/add_participant/
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        # Add validation logic here
        conversation.participants.add(user_id)
        return Response({'status': 'participant added'})

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Custom action to get messages for a specific conversation
        URL: /api/conversations/{id}/messages/
        """
        conversation = self.get_object()
        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Message operations
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter messages to only those in conversations where user is participant
        """
        user = self.request.user
        return Message.objects.filter(conversation__participants=user)

    def perform_create(self, serializer):
        """
        Automatically set sender to current user when creating message
        """
        serializer.save(sender=self.request.user)

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """
        Custom action to get unread messages for current user
        URL: /api/messages/unread/
        """
        unread_messages = self.get_queryset().filter(
            read=False
        ).exclude(sender=request.user)
        
        serializer = self.get_serializer(unread_messages, many=True)
        return Response(serializer.data)
      from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

app_name = 'messaging_app'

urlpatterns = [
    path('api/', include(router.urls)),
]

# Optional: Add API root view
urlpatterns += router.urls

from django.apps import AppConfig

class MessagingAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messaging_app'

python manage.py makemigrations
python manage.py migrate
rm db.sqlite3
rm app/migrations/00*.py
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
http://127.0.0.1:8000/

Add JWT Authentication + User Access Control
Step 1 — Install SimpleJWT

Run:
pip install djangorestframework-simplejwt

Step 2 — Update settings.py with JWT Authentication

Add/update the following:
INSTALLED_APPS += [
    "rest_framework",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        # Optional: keep session authentication if needed
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    )
}

from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

Step 3 — Add JWT URLs (project/urls.py)
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

Now you can log in with:
POST /api/token/
{ "username": "yourname", "password": "yourpassword" }

Step 4 — Ensure each user only accesses their own conversations/messages

To do this we lock down the querysets in your viewsets.

Assuming you have models like:
# messages/models.py
from django.db import models
from django.conf import settings

class Conversation(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL)

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

Step 5 — Restrict access in the ViewSets
Users only see conversations they belong to
Users only see messages in their own conversations
# messages/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only show conversations where the logged-in user is a participant
        return Conversation.objects.filter(participants=self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only messages from conversations the user belongs to
        return Message.objects.filter(
            conversation__participants=self.request.user
        )

    def perform_create(self, serializer):
        # Ensure sender = logged-in user
        serializer.save(sender=self.request.user)

This prevents users from accessing other people’s chats
This applies even if they guess the conversation ID
DRF automatically returns 404 if user is not a participant
Step 6 — Add ViewSets to urls.py

If using DRF router:
from rest_framework.routers import DefaultRouter
from messages.views import ConversationViewSet, MessageViewSet

router = DefaultRouter()
router.register("conversations", ConversationViewSet, basename="conversations")
router.register("messages", MessageViewSet, basename="messages")

urlpatterns += router.urls

TASK 0 is fully complete

we have:

✔ JWT authentication
✔ Token and refresh token endpoints
✔ Global API protection (IsAuthenticated)
✔ Users only access THEIR own conversations
✔ Users only access THEIR own messages

