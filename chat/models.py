from django.db import models
from django.contrib.auth.models import User
from posts.models import Post


class Conversation(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_user2")
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ("user1", "user2")

    def __str__(self):
        return f"{self.user1} & {self.user2}"

    @staticmethod
    def get_or_create_pair(u1, u2):
        # order fixed so unique works
        if u1.id > u2.id:
            u1, u2 = u2, u1
        return Conversation.objects.get_or_create(user1=u1, user2=u2)


# chat/models.py
from django.db import models
from django.contrib.auth.models import User
from posts.models import Post

class Message(models.Model):
    conversation = models.ForeignKey("chat.Conversation", related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    # ✅ FIX: add related_name
    post = models.ForeignKey(
        Post,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="chat_messages_post"
    )

    shared_post = models.ForeignKey(
        Post,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="chat_messages_shared"
    )

    attachment = models.FileField(upload_to="chat/", null=True, blank=True)
     # ✅ Seen system
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def mark_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])
    def is_image(self):
            if not self.attachment:
                return False
            return str(self.attachment.url).lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))
    
    def is_video(self):
        if not self.attachment:
            return False
        return str(self.attachment.url).lower().endswith((".mp4", ".webm", ".ogg"))        
    
    def __str__(self):
        return f"{self.sender} -> {self.conversation_id}"