Implementation: Message Notification System
Step 1: Define the Models (in messaging/models.py)
We need three models: Message, Notification, and we'll assume a standard Django User model is available.
# messaging/models.py
from django.db import models
from django.contrib.auth.models import User # Use Django's built-in User model

# 1. Message Model
class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}"

# 2. Notification Model
class Notification(models.Model):
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.text}"

Step 2: Create the Signal Receiver (in messaging/signals.py)
This file holds the event listener that creates a Notification every time a Message is successfully saved to the database.
# messaging/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification

@receiver(post_save, sender=Message)
def create_notification_on_new_message(sender, instance, created, **kwargs):
    """
    Listens for a post_save event on the Message model.
    If a NEW message (created=True) is saved, it automatically creates a notification
    for the message receiver.
    """
    if created:
        # Get the receiver user and the sender's username
        receiver = instance.receiver
        sender_username = instance.sender.username
        
        # Construct the notification text
        notification_text = f"New message from {sender_username}."
        
        # Create the Notification instance
        Notification.objects.create(
            user=receiver,
            message=instance,
            text=notification_text
        )
        print(f"Signal triggered: Notification created for {receiver.username}.")

Step 3: Connect the Signals (in messaging/apps.py)
To ensure Django loads and registers the signal handlers, we must import messaging.signals within the ready() method of the app's configuration.
# messaging/apps.py
from django.apps import AppConfig

class MessagingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messaging'
    
    def ready(self):
        # IMPORTANT: Import the signals file to register the handlers
        import messaging.signals

✅ Testing the Outcome
Once you have run python manage.py makemigrations and python manage.py migrate, you can test this in the Django shell:
# Assuming you have two users, 'alice' and 'bob'
>>> from django.contrib.auth.models import User
>>> from messaging.models import Message, Notification
>>> alice = User.objects.get(username='alice')
>>> bob = User.objects.get(username='bob')

# 1. Create a new message (This is the "sender")
>>> new_msg = Message.objects.create(sender=alice, receiver=bob, content="How are you?")
Signal triggered: Notification created for bob.

# 2. Check for the notification (This is the "receiver")
>>> bob.notifications.all()
<QuerySet [<Notification: Notification for bob: New message from alice.>]>

# The signal has successfully created the decoupled side-effect!



