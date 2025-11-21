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
