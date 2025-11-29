Set up basic caching for the messages view

1. Update settings.py With LocMemCache

Open:
messagingapp/messagingapp/settings.py

Add this (or replace your existing CACHES):
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

Why LocMemCache?

It stores cache in memory, inside the server process.

It’s the easiest and fastest option for development.

2. Cache the View That Displays Messages in a Conversation

Let’s say you have a view something like:
def conversation_messages(request, conversation_id):
    messages = Message.objects.filter(conversation_id=conversation_id)
    return render(request, "messages/conversation.html", {"messages": messages})

Now apply caching:
from django.views.decorators.cache import cache_page

@cache_page(60)   # Cache for 60 seconds
def conversation_messages(request, conversation_id):
    messages = Message.objects.filter(conversation_id=conversation_id)
    return render(request, "messages/conversation.html", {"messages": messages})

This means:

If a user opens this conversation:

Django will fetch messages from the database the first time

For the next 60 seconds the same response is served from the cache

Good for performance if your messages table is large

3. (Alternative) Decorate the URL Instead of the View

You can also cache via urls.py.
from django.urls import path
from django.views.decorators.cache import cache_page
from .views import conversation_messages

urlpatterns = [
    path(
        "conversation/<int:conversation_id>/",
        cache_page(60)(conversation_messages),
        name="conversation_messages"
    ),
]

Both methods work — choose the one your project style prefers.
⭐ Important Notes

✔ Each conversation ID is cached separately
→ /conversation/1/ has its own cache
→ /conversation/2/ has a different cache

✔ Cache only lasts 60 seconds
→ After that, Django refreshes and stores the new result

✔ Messages created within the 60-second window won’t appear immediately
→ This is normal for cached pages


