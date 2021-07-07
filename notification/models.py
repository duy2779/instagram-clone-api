from django.db import models

from accounts.models import User
from post.models import Post

class Notification(models.Model):
    
    CHOICES = (
        ('like', 'like'),
        ('comment', 'comment'),
        ('follow', 'follow'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name="notifications")
    notification_type = models.CharField(max_length=20, choices=CHOICES)
    seen = models.BooleanField(default=False)
    content = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.content
    
    
