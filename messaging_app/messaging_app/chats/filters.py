pagination + filtering for messages.
Step 1 — Install django-filter
Run:
pip install django-filter
Step 2 — Configure pagination + filtering in settings.py

Add this:
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,  # fetch 20 messages per page
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
}

✔ Automatically applies pagination and filtering to all compatible viewsets
✔ Messages API will now return 20 results per page with ?page=1, ?page=2

Step 3 — Create MessageFilter class (for filtering users & time range)

Create:
yourapp/filters.py

Add:
# yourapp/filters.py
import django_filters
from .models import Message

class MessageFilter(django_filters.FilterSet):
    # Filter messages sent by a specific user
    sender = django_filters.NumberFilter(field_name="sender__id")

    # Filter messages between date/time range
    start_date = django_filters.DateTimeFilter(
        field_name="timestamp", lookup_expr="gte"
    )
    end_date = django_filters.DateTimeFilter(
        field_name="timestamp", lookup_expr="lte"
    )

    class Meta:
        model = Message
        fields = ["sender", "start_date", "end_date"]

✔ This allows API calls like:

/messages/?sender=5 → all messages from user with id=5

/messages/?start_date=2024-01-01T00:00 → messages after date

/messages/?end_date=2024-01-07T23:59 → messages before date

/messages/?sender=3&start_date=2024-05-01T00:00 → combined filters
Step 4 — Apply filter to MessageViewSet

Modify your MessageViewSet:
# yourapp/views.py
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

from .models import Message
from .serializers import MessageSerializer
from .permissions import IsParticipantOfConversation
from .filters import MessageFilter


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsParticipantOfConversation]

    # add filters
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter

    def get_queryset(self):
        # User only sees messages in conversations they belong to
        return Message.objects.filter(
            conversation__participants=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

✔ Filtering now works
✔ Pagination applies automatically
✔ Security from Task 2 remains enforced

Testing checklist
Pagination test

Call:
GET /messages/?page=1

Should return:
{
  "count": 124,
  "next": "http://.../messages/?page=2",
  "previous": null,
  "results": [ ... 20 message objects ... ]
}

Filtering tests:
Filter by sender:
GET /messages/?sender=4

Filter by date range:
GET /messages/?start_date=2024-01-01T00:00&end_date=2024-01-31T23:59

Combine filters:
GET /messages/?sender=4&start_date=2024-02-10T00:00

Everything should still obey permission rules — user only sees messages from conversations they are part of.
