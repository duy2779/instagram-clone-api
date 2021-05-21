from django.db import models
from accounts.models import User


class Post(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, blank=False)
    caption = models.TextField()
    image = models.ImageField(null=False, blank=False)
    users_like = models.ManyToManyField(
        User, related_name="posts_like", blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.caption

    @property
    def likes_count(self):
        return self.users_like.all().count()

    @property
    def comments_count(self):
        return self.comments.all().count()


class PostComment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, blank=False)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment
