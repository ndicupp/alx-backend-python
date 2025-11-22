Restrict Access by Time Middleware
Requirement

Deny access outside 6 AM → 9 PM
Meaning:

Allowed time: 06:00 to 21:00

Forbidden time: 21:00 to 06:00

If request happens outside allowed hours, return:
HttpResponseForbidden("Access not allowed at this time")

Step 1: Create the middleware file

Create:
apps/core/middleware/restrict_time_middleware.py

Step 2: Implement RestrictAccessByTimeMiddleware
# apps/core/middleware/restrict_time_middleware.py

from datetime import datetime
from django.http import HttpResponseForbidden


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour

        # Allowed between 6 AM (6) and 9 PM (21)
        if not (6 <= current_hour < 21):
            return HttpResponseForbidden("Access not allowed at this time")

        return self.get_response(request)

✔ What this does:

Gets the current server hour

If hour is < 6 or >= 21, access is denied

Otherwise request continues
Step 3: Add Middleware to settings.py

Open:
config/settings.py

Add your middleware to the list:
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    # Your time restriction middleware
    "apps.core.middleware.restrict_time_middleware.RestrictAccessByTimeMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",
]

Place it after AuthenticationMiddleware if you want to check logged-in users;
otherwise, order doesn’t matter for this simple case.
Step 4: Run the server and test
python manage.py runserver

If the current time is outside 6 AM → 9 PM, any request should return:
403 Forbidden
Access not allowed at this time

If time is within allowed hours, everything works normally.
