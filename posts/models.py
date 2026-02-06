from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True)  # blank=True better
    image = models.ImageField(upload_to="posts/", blank=True, null=True)
    video = models.FileField(upload_to="reels/", blank=True, null=True)
    is_reel = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)

    likes = models.ManyToManyField(User, related_name="post_likes", blank=True)
    share_count = models.PositiveIntegerField(default=0)

    def like_count(self):
        return self.likes.count()

    def get_absolute_url(self):
        return reverse("post_detail", args=[self.id])

    def __str__(self):
        return f"{self.author.username}: {self.content[:30]}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:30]
