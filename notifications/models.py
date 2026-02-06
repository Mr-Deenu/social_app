from django.db import models
from django.contrib.auth.models import User
from posts.models import Post

class Notification(models.Model):
    NOTIF_TYPES = (
        ("like", "Like"),
        ("comment", "Comment"),
        ("follow", "Follow"),
        ("message", "Message"),
        ("share", "Share"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_notifications",null=True, blank= True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIF_TYPES)
    is_read = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} → {self.user} ({self.notification_type})"
