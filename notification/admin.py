from django.contrib import admin

from .models import Notification
# Register your models here.


class NotificationAdmin(admin.ModelAdmin):
    list_display = ("content", "user", "created_by", "created", "seen")


admin.site.register(Notification, NotificationAdmin)
