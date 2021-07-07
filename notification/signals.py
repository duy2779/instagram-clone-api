from django.db.models.signals import post_delete, post_save, pre_save

from accounts.models import User
from post.models import PostComment
from .models import Notification


def post_comment_created(sender, instance, created, **kwargs):
    if not created:
        return
    notification = Notification.objects.create(
        user = instance.post.user,
        created_by = instance.user,
        notification_type = 'comment',
        post = instance.post,
        content = f"{instance.user.username} added a comment to {instance.post.user.username}'s post"
    )
    
post_save.connect(post_comment_created, sender=PostComment)