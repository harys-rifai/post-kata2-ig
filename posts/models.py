from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class Topic(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Post(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("generated", "Generated"),
        ("scheduled", "Scheduled"),
        ("posting", "Posting"),
        ("published", "Published"),
        ("failed", "Failed"),
    )
    
    CATEGORY_CHOICES = (
        ("hidup", "Hidup"),
        ("ai", "AI & Teknologi"),
        ("astrology", "Astrologi & Kosmologi"),
    )

    title = models.CharField(max_length=255)
    topic = models.TextField()
    caption = models.TextField()
    hashtags = models.TextField()
    image_prompt = models.TextField()
    image = models.ImageField(upload_to="posts/", blank=True, null=True)
    publish_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="hidup")
    retry_count = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class InstagramConnection(models.Model):
    STATUS_CHOICES = (
        ("connected", "Connected"),
        ("disconnected", "Disconnected"),
        ("error", "Error"),
        ("checking", "Checking"),
    )

    username = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="disconnected")
    last_login = models.DateTimeField(blank=True, null=True)
    last_error = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.username} - {self.status}"


class Notification(models.Model):
    LEVEL_CHOICES = (
        ("info", "Info"),
        ("success", "Success"),
        ("warning", "Warning"),
        ("error", "Error"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications", null=True, blank=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="info")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
