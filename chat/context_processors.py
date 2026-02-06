from django.db.models import Q
from .models import Conversation, Message

def chat_unread(request):
    if not request.user.is_authenticated:
        return {"chat_unread_count": 0, "chat_unread_list": []}

    user = request.user
    convos = Conversation.objects.filter(Q(user1=user) | Q(user2=user))

    unread_qs = Message.objects.filter(
        conversation__in=convos,
        is_read=False
    ).exclude(sender=user).select_related("sender", "conversation").order_by("-created")

    chat_unread_count = unread_qs.count()
    chat_unread_list = unread_qs[:5]

    return {
        "chat_unread_count": chat_unread_count,
        "chat_unread_list": chat_unread_list
    }
