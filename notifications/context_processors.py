from .models import Notification

def unread_notifications(request):
    if request.user.is_authenticated:
        qs = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).order_by("-created")[:10]
        return {"unread_notifications": qs}
    return {"unread_notifications": []}


def notification_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return {"notification_count": count}
    return {"notification_count": 0}


def notification_data(request):
    if request.user.is_authenticated:
        unread_qs = Notification.objects.filter(user=request.user, is_read=False).order_by("-created")[:10]
        return {
            "unread_notifications": unread_qs,
            "notification_count": unread_qs.count(),
        }
    return {
        "unread_notifications": [],
        "notification_count": 0,
    }