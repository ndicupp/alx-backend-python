import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user extending Django's AbstractUser.
    Adds UUID primary key + extra fields from the schema.
    """

    ROLE_CHOICES = (
        ("guest", "Guest"),
        ("host", "Host"),
        ("admin", "Admin"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # AbstractUser already includes: first_name, last_name, email, password
    # So we add the extra fields from your schema:
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="guest")

    created_at = models.DateTimeField(auto_now_add=True)

    # Ensure email is unique as required by your schema
    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = ["email", "first_name", "last_name"]  # for createsuperuser

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
import uuid
from django.db import models
from django.conf import settings


class Conversation(models.Model):
    """
    Tracks which users are involved in a conversation.
    Supports multi-participant conversations via M2M.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="conversations"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id}"
import uuid
from django.db import models
from django.conf import settings


class Message(models.Model):
    """
    Message sent inside a conversation.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )

    conversation = models.ForeignKey(
        "Conversation",
        on_delete=models.CASCADE,
        related_name="messages"
    )

    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} in {self.conversation}"
