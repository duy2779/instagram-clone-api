from django.contrib import admin
from .models import Post, PostComment

# Register your models here.


class PostAdmin(admin.ModelAdmin):
    list_display = ("caption", "user", "likes_count",
                    "comments_count", "created")


admin.site.register(Post, PostAdmin)
admin.site.register(PostComment)
