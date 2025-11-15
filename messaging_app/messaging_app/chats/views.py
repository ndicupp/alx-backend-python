from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from accounts.serializers import UserSerializer
from accounts.models import User


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, retrieving, and creating conversations.
    """

    queryset = Conversation.objects.all().prefetch_related("participants", "messages__sender")
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Create a new conversation with participants.
        Expecting participant IDs in request.data['participant_ids']
        """
        participant_ids = request.data.get("participant_ids", [])
        if not participant_ids:
            return Response(
                {"detail": "participant_ids is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        participants = User.objects.filter(id__in=participant_ids)
        if not participants.exists():
            return Response(
                {"detail": "No valid participants found."},
                status=status.HTTP_400_BAD_REQUEST
            )

        conversation = Conversation.objects.create()
        conversation.participants.set(participants)
        conversation.save()

        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing messages and sending a message to an existing conversation.
    """

    queryset = Message.objects.all().select_related("sender", "conversation")
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Send a message to an existing conversation.
        Expecting 'conversation_id' and 'message_body' in request.data
        """
        conversation_id = request.data.get("conversation_id")
        message_body = request.data.get("message_body")

        if not conversation_id or not message_body:
            return Response(
                {"detail": "conversation_id and message_body are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response(
                {"detail": "Conversation not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        message = Message.objects.create(
            sender=request.user,
            conversation=conversation,
            message_body=message_body
        )

        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


Create Conversation
POST /api/v1/conversations/
{
    "participant_ids": ["uuid-of-user-1", "uuid-of-user-2"]
}

Send Message
POST /api/v1/messages/
{
    "conversation_id": "uuid-of-conversation",
    "message_body": "Hello there!"
}

Database Specification

Entities and Attributes
Message

    message_id (Primary Key, UUID, Indexed)
    sender_id (Foreign Key, references User(user_id))
    message_body (TEXT, NOT NULL)
    sent_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
Conversation

conversation_id (Primary Key, UUID, Indexed)
participants_id (Foreign Key, references User(user_id)
created_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

Constraints:

    User Table: Unique constraint on email, non-null constraints on required fields.
    Property Table: Foreign key constraint on host_id, non-null constraints on essential attributes.
    Booking Table: Foreign key constraints on property_id and user_id, status must be one of pending, confirmed, or canceled.
    Payment Table: Foreign key constraint on booking_id, ensuring payment is linked to valid bookings.
    Review Table: Constraints on rating values and foreign keys for property_id and user_id.
    Message Table: Foreign key constraints on sender_id and recipient_id.
Indexing:

**Primary Keys:** Indexed automatically.
**Additional Indexes:** Indexes on email (User), property_id (Property and Booking), and booking_id (Booking and Payment)
