from django.db import models
from django.contrib.auth.models import User


class FriendRequest(models.Model):
    sender = models.ForeignKey(User, related_name='sender', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='receiver', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='pending')
    created = models.DateTimeField(auto_now_add=True)

