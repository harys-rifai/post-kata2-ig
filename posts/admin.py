from django.contrib import admin
from .models import Post, InstagramConnection


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "publish_at", "retry_count", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "topic", "caption")
    readonly_fields = ("created_at", "updated_at", "retry_count")
    fields = (
        "title",
        "topic",
        "caption",
        "hashtags",
        "image_prompt",
        "image",
        "publish_at",
        "status",
        "retry_count",
        "error_message",
        "created_at",
        "updated_at",
    )


@admin.register(InstagramConnection)
class InstagramConnectionAdmin(admin.ModelAdmin):
    list_display = ("username", "status", "is_active", "last_login", "updated_at")
    list_filter = ("status", "is_active", "created_at")
    search_fields = ("username",)
    readonly_fields = ("created_at", "updated_at", "last_login")
    fields = (
        "username",
        "status",
        "is_active",
        "last_login",
        "last_error",
        "created_at",
        "updated_at",
    )
