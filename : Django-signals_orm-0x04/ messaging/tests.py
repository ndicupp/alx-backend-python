Step-by-Step Implementation
Step 1: Create the Message Model
First, let's create the Message model. Create or update models.py in your app:
# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Message(models.Model):
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='received_messages'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']  # Show newest messages first

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"

Step 2: Create the Notification Model
Now, let's create the Notification model in the same models.py:
# models.py (continued)
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('message', 'New Message'),
        ('system', 'System Notification'),
        ('alert', 'Alert'),
    ]

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    message = models.ForeignKey(
        Message, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        null=True, 
        blank=True
    )
    notification_type = models.CharField(
        max_length=20, 
        choices=NOTIFICATION_TYPES, 
        default='message'
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user}: {self.title}"

Step 3: Create the Signal Handler
Create a new file signals.py in your app directory:
# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Message, Notification

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Signal receiver that creates a notification when a new message is created.
    """
    if created:  # Only trigger for new messages, not updates
        # Create the notification
        notification = Notification.objects.create(
            user=instance.receiver,
            message=instance,
            notification_type='message',
            title=f"New message from {instance.sender.username}",
            content=f"You have received a new message: {instance.content[:100]}..."  # Preview
        )
        
        # Optional: Send email notification (uncomment if needed)
        # send_email_notification(instance, notification)
        
        print(f"Notification created for {instance.receiver.username}")

def send_email_notification(message, notification):
    """
    Optional: Send email notification to the user
    """
    subject = f"New message from {message.sender.username}"
    message_content = f"""
    Hello {message.receiver.username},
    
    You have received a new message from {message.sender.username}:
    
    "{message.content}"
    
    Login to your account to view and reply.
    
    Best regards,
    Your App Team
    """
    
    send_mail(
        subject,
        message_content,
        settings.DEFAULT_FROM_EMAIL,
        [message.receiver.email],
        fail_silently=True,
    )

Step 4: Register the Signals
Update your app's apps.py to register the signals:
# apps.py
from django.apps import AppConfig

class YourAppNameConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'your_app_name'  # Replace with your actual app name

    def ready(self):
        # Import and register signals
        import your_app_name.signals  # Replace with your actual app name


  Step 5: Create and Run Migrations
  # Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

Step 6: Test the Implementation
Let's create a simple test to verify everything works. Create tests.py:
# tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification

class SignalTestCase(TestCase):
    def setUp(self):
        # Create test users
        self.sender = User.objects.create_user(
            username='sender', 
            email='sender@test.com', 
            password='testpass123'
        )
        self.receiver = User.objects.create_user(
            username='receiver', 
            email='receiver@test.com', 
            password='testpass123'
        )

    def test_message_creates_notification(self):
        """Test that creating a message automatically creates a notification"""
        # Check initial state
        initial_notification_count = Notification.objects.count()
        
        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello, this is a test message!"
        )
        
        # Check that a notification was created
        final_notification_count = Notification.objects.count()
        self.assertEqual(final_notification_count, initial_notification_count + 1)
        
        # Verify notification details
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message, message)
        self.assertEqual(notification.notification_type, 'message')
        self.assertIn(self.sender.username, notification.title)
        
    def test_notification_only_on_creation(self):
        """Test that notifications are only created on message creation, not update"""
        # Create a message (should create notification)
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )
        
        initial_count = Notification.objects.count()
        
        # Update the message (should NOT create another notification)
        message.content = "Updated content"
        message.save()
        
        final_count = Notification.objects.count()
        self.assertEqual(final_count, initial_count)  # Count should not change

    Run the tests:
    python manage.py test your_app_name

    Step 7: Create Admin Interface (Optional but Recommended)
Update admin.py to make it easy to manage messages and notifications:
# admin.py
from django.contrib import admin
from .models import Message, Notification

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'content_preview', 'timestamp', 'is_read']
    list_filter = ['timestamp', 'is_read']
    search_fields = ['content', 'sender__username', 'receiver__username']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title_preview', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'content', 'user__username']
    
    def title_preview(self, obj):
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    title_preview.short_description = 'Title'

Step 8: Manual Testing
You can also test manually using Django shell:
python manage.py shell

# In Django shell
from django.contrib.auth.models import User
from your_app.models import Message, Notification

# Create users
user1 = User.objects.create_user('test1', 'test1@example.com', 'password')
user2 = User.objects.create_user('test2', 'test2@example.com', 'password')

# Create a message - this should automatically create a notification
message = Message.objects.create(
    sender=user1,
    receiver=user2,
    content="This is a test message from the shell!"
)

# Check if notification was created
notifications = Notification.objects.filter(user=user2)
print(f"User2 has {notifications.count()} notifications")
for notification in notifications:
    print(f"- {notification.title}: {notification.content}")

# Exit shell
exit()


Key Concepts Demonstrated
✅ Django Signals: Using post_save to trigger actions on model creation
✅ Event-Driven Architecture: Decoupling notification logic from message creation
✅ Model Relationships: ForeignKey relationships between User, Message, and Notification
✅ Signal Registration: Properly connecting signals in ready() method
✅ Conditional Logic: Only creating notifications for new messages (created=True)

Expected Behavior
When you create a new Message:

Signal triggers automatically after the Message is saved

Notification is created for the message receiver

Email is sent (if you uncomment that part)

Console message confirms the notification was created
