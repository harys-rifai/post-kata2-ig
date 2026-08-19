import json
import os
import random
import requests
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.core.files.base import ContentFile
from PIL import Image as PILImage
from io import BytesIO
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import Post, InstagramConnection, Topic, Notification
from ai.services import AIService, InstagramAutomationService


class PostService:
    @staticmethod
    def generate_content(topic=None):
        if topic is None:
            topics = list(Topic.objects.values_list("name", flat=True))
            if topics:
                topic = random.choice(topics)
            else:
                topic = "AI"
        result = AIService.generate_caption(topic)
        post = Post.objects.create(
            title=result.get("title", topic),
            topic=topic,
            caption=result.get("caption", ""),
            hashtags=result.get("hashtags", ""),
            image_prompt=result.get("image_prompt", ""),
            category=result.get("category", "hidup"),
            status="generated",
        )
        return post

    @staticmethod
    def generate_image_for_post(post):
        try:
            prompt_text = post.image_prompt or post.title or post.topic or "Instagram Post"
            image_data, image_url = AIService.generate_image(prompt_text)
            image_data = PostService._process_image(image_data)
            filename = f"post_{post.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}.png"
            post.image.save(filename, ContentFile(image_data), save=False)
            post.save()
            return True
        except requests.exceptions.HTTPError as e:
            if "No credentials" in str(e) or "Provider" in str(e) and "does not support" in str(e):
                return PostService._generate_placeholder_image(post.title or post.topic, post.category)
            else:
                raise
        except Exception as e:
            post.error_message = str(e)
            try:
                image_data = PostService._generate_placeholder_image(post.title or post.topic, post.category)
                filename = f"post_{post.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}.png"
                post.image.save(filename, ContentFile(image_data), save=False)
                post.save()
                return True
            except Exception as placeholder_error:
                post.error_message = f"{str(e)}; placeholder fallback also failed: {str(placeholder_error)}"
                post.save()
                return False

    @staticmethod
    def _process_image(image_data):
        try:
            img = PILImage.open(BytesIO(image_data))
            if img.mode in ("RGBA", "LA"):
                background = PILImage.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            img.thumbnail((1024, 1024))
            buffer = BytesIO()
            img.save(buffer, format="PNG", optimize=True)
            return buffer.getvalue()
        except Exception as e:
            raise Exception(f"Image processing failed: {str(e)}")

    @staticmethod
    def _generate_placeholder_image(text, category="hidup"):
        img_data, _ = AIService._generate_placeholder_image(text, category)
        return img_data

    @staticmethod
    def schedule_post(post, publish_at):
        post.publish_at = publish_at
        post.status = "scheduled"
        post.save()

    @staticmethod
    def get_pending_scheduled():
        now = timezone.now()
        return Post.objects.filter(status="scheduled", publish_at__lte=now)

    @staticmethod
    def get_next_scheduled():
        now = timezone.now()
        return Post.objects.filter(status="scheduled", publish_at__gt=now).order_by("publish_at").first()

    @staticmethod
    def mark_posting(post):
        post.status = "posting"
        post.save()

    @staticmethod
    def mark_published(post):
        post.status = "published"
        post.save()

    @staticmethod
    def mark_failed(post, error_message=""):
        post.status = "failed"
        post.retry_count += 1
        post.error_message = error_message
        post.save()

    @staticmethod
    def should_retry(post, max_retries=5):
        if post.retry_count >= max_retries:
            return False
        delay = 2 ** post.retry_count
        if post.updated_at:
            next_retry = post.updated_at + timedelta(minutes=delay)
            return timezone.now() >= next_retry
        return True

    @staticmethod
    def update_post(post, title=None, topic=None, caption=None, hashtags=None, image_prompt=None, publish_at=None, status=None):
        if title is not None:
            post.title = title
        if topic is not None:
            post.topic = topic
        if caption is not None:
            post.caption = caption
        if hashtags is not None:
            post.hashtags = hashtags
        if image_prompt is not None:
            post.image_prompt = image_prompt
        if publish_at is not None:
            post.publish_at = publish_at
        if status is not None:
            post.status = status
        post.save()
        return post

    @staticmethod
    def delete_post(post):
        if post.image:
            post.image.delete(save=False)
        post.delete()


class InstagramConnectionService:
    @staticmethod
    def get_or_create_connection(username):
        connection, created = InstagramConnection.objects.get_or_create(
            username=username,
            defaults={"status": "disconnected", "is_active": False},
        )
        return connection

    @staticmethod
    def mark_connected(username):
        connection = InstagramConnectionService.get_or_create_connection(username)
        connection.status = "connected"
        connection.is_active = True
        connection.last_login = timezone.now()
        connection.last_error = None
        connection.save()
        return connection

    @staticmethod
    def mark_disconnected(username, error=None):
        connection = InstagramConnectionService.get_or_create_connection(username)
        connection.status = "disconnected"
        connection.is_active = False
        connection.last_error = error
        connection.save()
        return connection

    @staticmethod
    def mark_error(username, error):
        connection = InstagramConnectionService.get_or_create_connection(username)
        connection.status = "error"
        connection.is_active = False
        connection.last_error = error
        connection.save()
        return connection

    @staticmethod
    def get_active_connection():
        return InstagramConnection.objects.filter(is_active=True).first()

    @staticmethod
    def test_connection():
        try:
            p, browser, context = InstagramAutomationService._get_browser_context()
            page = context.new_page()
            success = InstagramAutomationService.login(page)
            context.close()
            browser.close()
            p.stop()
            if success:
                return True, None
            return False, "Login failed"
        except Exception as e:
            return False, str(e)


class NotificationService:
    @staticmethod
    def create_notification(user, title, message, level="info"):
        Notification.objects.create(
            user=user,
            title=title,
            message=message,
            level=level,
        )

    @staticmethod
    def create_system_notification(title, message, level="info"):
        users = User.objects.filter(is_active=True)
        for user in users:
            Notification.objects.create(
                user=user,
                title=title,
                message=message,
                level=level,
            )