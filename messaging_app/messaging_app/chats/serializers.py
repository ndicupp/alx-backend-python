UserSerializer

Exposes user data safely

Does not expose password

Follows Django best practices

from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

apps/chat/serializers.py

We build three serializers:

MessageSerializer

ConversationParticipantSerializer (for clean nested output)

ConversationSerializer (includes nested participants + nested messages)

MessageSerializer

from rest_framework import serializers
from .models import Message, Conversation
from accounts.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "sender",
            "message_body",
            "sent_at",
        ]
        read_only_fields = ["id", "sent_at", "sender"]

ConversationSerializer
Includes:

A list of participants (nested UserSerializer)

A list of messages (nested MessageSerializer)

Uses messages = MessageSerializer(many=True, read_only=True)

This is the standard DRF approach for nested relations.

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            "id",
            "participants",
            "messages",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

How nested data works now
When you GET a conversation:

{
  "id": "c2a1e5ab-23d2-43bd-88a8-05c6797cbe78",
  "participants": [
    {
      "id": "9ddc8e79-5b65-4d25-a845-875d9539dcd4",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "role": "guest"
    }
  ],
  "messages": [
    {
      "id": "0fa3e582-c891-4271-b8b5-f86df0c8dfea",
      "sender": {
        "id": "9ddc8e79-5b65-4d25-a845-875d9539dcd4",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "role": "guest"
      },
      "message_body": "Hello!",
      "sent_at": "2025-02-12T10:23:51Z"
    }
  ],
  "created_at": "2025-02-12T10:20:00Z"
}


Database Specification

Entities and Attributes

User

    user_id (Primary Key, UUID, Indexed)
    first_name (VARCHAR, NOT NULL)
    last_name (VARCHAR, NOT NULL)
    email (VARCHAR, UNIQUE, NOT NULL)
    password_hash (VARCHAR, NOT NULL)
    phone_number (VARCHAR, NULL)
    role (ENUM: 'guest', 'host', 'admin', NOT NULL)
    created_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
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

python manage.py makemigrations
python manage.py migrate
rm db.sqlite3
rm app/migrations/00*.py
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
http://127.0.0.1:8000/

