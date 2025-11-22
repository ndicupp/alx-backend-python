Create Request Logging Middleware
Step 1: Create the middleware file

Inside your project:
Django-Middleware-0x03/
   apps/
      core/
         middleware/
             request_logging_middleware.py   ← create this file
If your project doesn’t have /middleware folder yet, create it.
  Step 2: Write the RequestLoggingMiddleware

Here is the correct and complete middleware class:
  # apps/core/middleware/request_logging_middleware.py

import logging
from datetime import datetime

# Configure a logger for middleware
logger = logging.getLogger("request_logger")


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "AnonymousUser"

        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"

        logger.info(log_message)

        return self.get_response(request)

Step 3: Configure Logging in settings.py

Still in your project, open:
config/settings.py

Add a logging configuration if it doesn’t exist yet:
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "handlers": {
        "request_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "request_logs.log",
        },
    },

    "loggers": {
        "request_logger": {
            "handlers": ["request_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

This creates a log file at:
request_logs.log

in your project root.
Step 4: Add Middleware to MIDDLEWARE in settings.py

Inside config/settings.py, find MIDDLEWARE, and add this line:
MIDDLEWARE = [
    # Django default middleware...
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",

    # Your custom middleware
    "apps.core.middleware.request_logging_middleware.RequestLoggingMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

Make sure it comes after AuthenticationMiddleware if you want correct request.user.

But for logging basic paths, it can be anywhere.
Step 5: Run the Server

In terminal:
python manage.py runserver

Then visit any URL:

http://localhost:8000/

http://localhost:8000/admin

any API endpoint

Check request_logs.log — it should show entries like:
2025-02-05 14:22:10.123456 - User: AnonymousUser - Path: /admin/login/
2025-02-05 14:22:15.876543 - User: Patrick - Path: /api/messages/


