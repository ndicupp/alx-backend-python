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

JWT authentication
Token and refresh token endpoints
Global API protection (IsAuthenticated)
Users only access THEIR own conversations
Users only access THEIR own messages

Creating and Applying Custom Permission Classes.
    Implementing IsParticipantOfConversation
I need to define this custom permission in a file like myapp/permissions.py. This class will contain the logic to check both general authentication and the specific participation requirement.

1. Define the Custom Permission
The custom permission class will override both the has_permission and has_object_permission methods.

has_permission(self, request, view): Checks if the user is generally allowed to access the list view (GET on /messages/) or create view (POST on /messages/).

has_object_permission(self, request, view, obj): Checks if the user is allowed to interact with a specific message object (GET, PUT, DELETE on /messages/{id}/).

# yourapp/permissions.py

from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to allow only authenticated users 
    who are participants in a conversation to access the messages.
    """

    def has_permission(self, request, view):
        # 1. Allow access only if the user is authenticated
        if not request.user or not request.user.is_authenticated:
            # Deny access if user is not logged in
            return False 
        
        # For list views or creation (POST), we might check additional 
        # parameters (e.g., the conversation ID in the request data/URL).
        # For simplicity here, we rely on has_object_permission for granular checks.
        return True

    def has_object_permission(self, request, view, obj):
        # The 'obj' here is the Message instance, which is linked to a Conversation.
        # We assume the Message model has a ForeignKey to a Conversation model, 
        # and the Conversation model has a many-to-many field or related set 
        # for 'participants'.

        # Example structure:
        # obj (Message) -> obj.conversation (Conversation) 
        # -> obj.conversation.participants (User list)

        if not hasattr(obj, 'conversation'):
             # If the object doesn't have a conversation link (e.g., if checking 
             # permission on the Conversation model itself), handle appropriately.
             return False

        # 2. Check if the authenticated user is one of the participants 
        # in the message's related conversation.
        conversation = obj.conversation
        return request.user in conversation.participants.all()

2.Apply Custom Permissions to ViewSets
Next, apply this custom permission to the relevant ViewSet (e.g., a MessageViewSet).
# yourapp/views.py

from rest_framework import viewsets
from .permissions import IsParticipantOfConversation
# from .models import Message, Conversation, ... (your models)

class MessageViewSet(viewsets.ModelViewSet):
    # This ViewSet handles all CRUD operations for messages (send, view, update, delete)
    queryset = Message.objects.all() 
    serializer_class = MessageSerializer
    
    # Apply the custom permission class
    permission_classes = [IsParticipantOfConversation]
    
    # You might also override 'get_queryset' to ensure users can 
    # only see messages in conversations they belong to in the list view.
    def get_queryset(self):
        # Filter the list of messages to only include those 
        # where the request user is a participant in the conversation.
        # (Assuming 'participants' is the M2M field on the Conversation model)
        return Message.objects.filter(
            conversation__participants=self.request.user
        ).distinct()

3. Update settings.py for Default Permissions
To enforce a high level of security across your entire API by default, set the global default permissions in settings.py. This ensures that unless a permission_classes attribute is explicitly set on a ViewSet, only authenticated users have access.
    # settings.py

# ... other settings

REST_FRAMEWORK = {
    # Set the default permission class for all views
    'DEFAULT_PERMISSION_CLASSES': [
        # This globally enforces that a user MUST be authenticated 
        # to access ANY API endpoint.
        'rest_framework.permissions.IsAuthenticated',
    ],

    # ... other DRF settings (like authentication classes, etc.)
}

By applying this global setting, you meet the first part of your requirement ("Allow only authenticated users to access the API") as a baseline, and your custom IsParticipantOfConversation then provides the essential object-level filtering on top of that baseline.


