Step 1: Create the Custom Middleware File
You need to create the file at the specified path: Django-Middleware-0x03/chats/middleware.py.

This code uses Django's timezone utility for robustness and implements the short-circuiting logic required.

Django-Middleware-0x03/chats/middleware.py
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.urls import reverse

class RestrictAccessByTimeMiddleware:
    """
    Middleware to restrict access to the application outside of standard 
    operating hours (9 AM to 6 PM).
    """

    def __init__(self, get_response):
        """
        One-time configuration and initialization. Stores the next callable.
        """
        self.get_response = get_response
        
        # Define the allowed access window (hours in 24-hour format)
        self.START_HOUR = 9   # 9:00 AM
        self.END_HOUR = 18    # 6:00 PM (18:00), access is denied at 18:00:00

    def __call__(self, request):
        """
        The main request/response processing logic.
        """
        # 1. Get the current time using Django's timezone utility
        # This returns a time-aware datetime object
        current_time = timezone.now()
        current_hour = current_time.hour

        # 2. Check if the current time is OUTSIDE the allowed window (9:00 to 17:59)
        is_restricted_hour = (
            current_hour < self.START_HOUR or  # Before 9 AM
            current_hour >= self.END_HOUR      # At or after 6 PM
        )
        
        # 3. Restrict Access: Check if the request is trying to access the 'chats' app
        # This assumes the 'chats' app URLs start with a common path, e.g., '/chats/'
        # NOTE: For a real project, you'd check for a specific URL prefix like request.path.startswith('/chats/')
        # However, for this project, we'll assume ALL traffic is for the chats app 
        # unless more specific URL-checking is requested.
        
        if is_restricted_hour:
            # Short-circuit the request by returning an immediate HttpResponse
            return HttpResponseForbidden(
                "Access Denied: The messaging service is only available "
                f"between {self.START_HOUR}:00 and {self.END_HOUR}:00 (server time)."
            )

        # 4. Allow Access: If the time is within the allowed window, call the next component
        response = self.get_response(request)

        # Code here would run on the response coming back (post-view)

        return response

Step 2: Configure the MIDDLEWARE Stack
Now you must register your custom middleware in your project's settings.py. It should be placed early in the list, before most of the security and session middleware that may rely on the request succeeding.

settings.py Update
Locate the MIDDLEWARE list in your settings.py file and add the full Python path to your new class.
# settings.py

MIDDLEWARE = [
    # Built-in Django Middleware (keep these in order)
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    
    # -------------------------------------------------------------
    # YOUR CUSTOM MIDDLEWARE GOES HERE
    # Path: <app_name>.<module_name>.<class_name>
    'chats.middleware.RestrictAccessByTimeMiddleware', 
    # -------------------------------------------------------------
    
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
Project Completion Summary
By completing these steps, you have successfully:

Created a custom middleware class (RestrictAccessByTimeMiddleware).

Used django.utils.timezone to reliably check the current server hour.

Implemented a conditional check to see if the hour is outside the allowed window.

Demonstrated short-circuiting by returning an HttpResponseForbidden (403) to immediately block the request from reaching the view.

Correctly configured the settings.py file to activate the new middleware.


Step 1: Set Up Caching and Constants
First, ensure your project has a cache backend configured in settings.py. For a development environment, Django's default in-memory cache is sufficient.

settings.py (Required Setup)
# settings.py

# Configure the default in-memory cache (suitable for development)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-rate-limit-key',
    }
}

# Define Rate Limiting Constants
RATE_LIMIT_MESSAGES = 5      # Max messages allowed
RATE_LIMIT_WINDOW = 60       # Time window in seconds (1 minute)

Step 2: Create the Middleware Class
Create the file at the specified path: Django-Middleware-0x03/chats/middleware.py and add the new class (RateLimitingMiddleware or OffensiveLanguageMiddleware based on your project requirements—I'll use the latter as requested by the prompt).

Django-Middleware-0x03/chats/middleware.py
import time
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseForbidden

class OffensiveLanguageMiddleware:
    """
    Middleware to implement rate limiting on chat messages (POST requests)
    based on the user's IP address. Limits to 5 messages per 60 seconds.
    
    NOTE: The name (OffensiveLanguageMiddleware) is kept as requested, 
    but the logic implements Rate Limiting.
    """

    def __init__(self, get_response):
        """Initializes the middleware and loads settings."""
        self.get_response = get_response
        self.RATE_LIMIT_MESSAGES = getattr(settings, 'RATE_LIMIT_MESSAGES', 5)
        self.RATE_LIMIT_WINDOW = getattr(settings, 'RATE_LIMIT_WINDOW', 60)

    def __call__(self, request):
        """Processes the incoming request."""
        
        # 1. Identify Requests to Track
        # We only care about chat messages, which are typically POST requests.
        if request.method != 'POST':
            return self.get_response(request)

        # 2. Get the User Identifier (IP Address)
        # It's common practice to look behind proxies using X-Forwarded-For
        # For simple testing, use REMOTE_ADDR.
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_address:
            # Take the first IP in the list if behind multiple proxies
            ip_address = ip_address.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')
            
        # Create a unique cache key for this user's rate limit data
        cache_key = f'rate_limit:{ip_address}'
        
        # 3. Retrieve or Initialize Rate Data from Cache
        # The cache stores a list of timestamps for the last messages sent.
        timestamps = cache.get(cache_key, [])
        current_timestamp = time.time()

        # 4. Clean Up Old Timestamps
        # Filter out all timestamps older than the rate limit window (60 seconds)
        # Only keep records of messages sent within the window.
        recent_timestamps = [
            t for t in timestamps 
            if t > current_timestamp - self.RATE_LIMIT_WINDOW
        ]

        # 5. Check Rate Limit
        if len(recent_timestamps) >= self.RATE_LIMIT_MESSAGES:
            # Limit exceeded: Short-circuit and deny access
            return HttpResponseForbidden(
                f"Rate limit exceeded. You can only send {self.RATE_LIMIT_MESSAGES} "
                f"messages every {self.RATE_LIMIT_WINDOW} seconds."
            )
        
        # 6. Update and Store Rate Data (Limit not exceeded)
        # Add the current timestamp to the list of recent messages
        recent_timestamps.append(current_timestamp)
        
        # Update the cache with the new list of timestamps. 
        # We set the timeout to the full window to ensure the key persists
        # as long as we might need to check against it.
        cache.set(
            cache_key, 
            recent_timestamps, 
            timeout=self.RATE_LIMIT_WINDOW
        )
        
        # 7. Proceed to View
        # If not blocked, call the next component in the chain
        response = self.get_response(request)

        return response

Step 3: Configure the MIDDLEWARE Stack
Add the new middleware to your settings.py. It should be placed after the common middleware but before any view-specific logic. Since it uses request.META for the IP, its position is relatively flexible, but before authentication or session logic is a good defensive practice.

    # settings.py

MIDDLEWARE = [
    # ... previous middleware ...
    
    'django.middleware.common.CommonMiddleware',
    
    # --------------------------------------------------------------------------
    # Add your custom middleware here
    # 1. Time restriction (Task 1)
    'chats.middleware.RestrictAccessByTimeMiddleware', 
    
    # 2. Rate Limiting (Task 2) - Placed early to block high-frequency bots
    'chats.middleware.OffensiveLanguageMiddleware', 
    # --------------------------------------------------------------------------
    
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # ... rest of the middleware ...
]

This implementation ensures that every POST request increments the counter for that specific IP address within the cache, and any subsequent request that exceeds the count within the 60-second window is immediately blocked with a 403 Forbidden response.



    

