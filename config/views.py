from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from django.conf import settings as django_settings
from datetime import timedelta
from posts.models import Post, InstagramConnection
from posts.services import PostService, InstagramConnectionService
import logging
import requests

logger = logging.getLogger(__name__)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, "login.html", {"error": "Invalid username or password"})
    
    return render(request, "login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    total_posts = Post.objects.count()
    published_posts = Post.objects.filter(status="published").count()
    scheduled_posts = Post.objects.filter(status="scheduled").count()
    failed_posts = Post.objects.filter(status="failed").count()
    pending_posts = Post.objects.filter(status="generated").count()
    
    week_ago = timezone.now() - timedelta(days=7)
    recent_posts = Post.objects.filter(created_at__gte=week_ago).order_by("-created_at")[:20]
    
    today = timezone.now().date()
    today_posts = Post.objects.filter(created_at__date=today).count()
    
    ig_connection = InstagramConnectionService.get_active_connection()
    
    context = {
        "total_posts": total_posts,
        "published_posts": published_posts,
        "scheduled_posts": scheduled_posts,
        "failed_posts": failed_posts,
        "pending_posts": pending_posts,
        "today_posts": today_posts,
        "recent_posts": recent_posts,
        "ig_connection": ig_connection,
    }
    return render(request, "dashboard.html", context)


@login_required
def posts_view(request):
    all_posts = Post.objects.all().order_by("-created_at")[:100]
    context = {
        "posts": all_posts,
    }
    return render(request, "posts.html", context)


@login_required
def post_create_view(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        topic = request.POST.get("topic", "").strip()
        caption = request.POST.get("caption", "").strip()
        hashtags = request.POST.get("hashtags", "").strip()
        image_prompt = request.POST.get("image_prompt", "").strip()
        publish_at = request.POST.get("publish_at", "").strip()
        status = request.POST.get("status", "draft")
        
        if not title or not topic:
            return render(request, "post_form.html", {
                "error": "Title and topic are required",
                "post": None,
            })
        
        post = Post.objects.create(
            title=title,
            topic=topic,
            caption=caption,
            hashtags=hashtags,
            image_prompt=image_prompt,
            status=status,
            publish_at=publish_at if publish_at else None,
        )
        
        if status == "scheduled" and publish_at:
            from django.utils.dateparse import parse_datetime
            post.publish_at = parse_datetime(publish_at)
            post.save()
        
        logger.info(f"User {request.user.username} created post: {post.id}")
        return redirect("posts")
    
    return render(request, "post_form.html", {"post": None})


@login_required
def post_edit_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        topic = request.POST.get("topic", "").strip()
        caption = request.POST.get("caption", "").strip()
        hashtags = request.POST.get("hashtags", "").strip()
        image_prompt = request.POST.get("image_prompt", "").strip()
        publish_at = request.POST.get("publish_at", "").strip()
        status = request.POST.get("status", "draft")
        
        if not title or not topic:
            return render(request, "post_form.html", {
                "error": "Title and topic are required",
                "post": post,
            })
        
        post.title = title
        post.topic = topic
        post.caption = caption
        post.hashtags = hashtags
        post.image_prompt = image_prompt
        post.status = status
        
        if publish_at:
            from django.utils.dateparse import parse_datetime
            post.publish_at = parse_datetime(publish_at)
        else:
            post.publish_at = None
        
        post.save()
        logger.info(f"User {request.user.username} updated post: {post.id}")
        return redirect("posts")
    
    return render(request, "post_form.html", {"post": post})


@login_required
def post_delete_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == "POST":
        post_id = post.id
        PostService.delete_post(post)
        logger.info(f"User {request.user.username} deleted post: {post_id}")
        return redirect("posts")
    
    return render(request, "post_confirm_delete.html", {"post": post})


@login_required
def schedule_view(request):
    scheduled_posts = Post.objects.filter(status="scheduled").order_by("publish_at")[:50]
    failed_posts = Post.objects.filter(status="failed").order_by("-updated_at")[:50]
    context = {
        "scheduled_posts": scheduled_posts,
        "failed_posts": failed_posts,
    }
    return render(request, "schedule.html", context)


@login_required
def schedule_create_view(request):
    if request.method == "POST":
        post_id = request.POST.get("post_id")
        publish_at = request.POST.get("publish_at", "").strip()
        
        if not post_id or not publish_at:
            return render(request, "schedule_form.html", {
                "error": "Post and publish time are required",
                "posts": Post.objects.filter(status__in=["generated", "draft"]).order_by("-created_at"),
            })
        
        post = get_object_or_404(Post, pk=post_id)
        from django.utils.dateparse import parse_datetime
        post.publish_at = parse_datetime(publish_at)
        post.status = "scheduled"
        post.save()
        
        logger.info(f"User {request.user.username} scheduled post: {post.id}")
        return redirect("schedule")
    
    posts = Post.objects.filter(status__in=["generated", "draft"]).order_by("-created_at")
    return render(request, "schedule_form.html", {"posts": posts})


@login_required
def schedule_delete_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == "POST":
        post.status = "draft"
        post.publish_at = None
        post.save()
        logger.info(f"User {request.user.username} unscheduled post: {post.id}")
        return redirect("schedule")
    
    return render(request, "schedule_confirm_delete.html", {"post": post})


@login_required
def generate_view(request):
    from posts.services import TOPICS
    
    result = None
    error = None
    
    if request.method == "POST":
        topic = request.POST.get("topic")
        custom_topic = request.POST.get("custom_topic", "").strip()
        
        if custom_topic:
            topic = custom_topic
        elif not topic:
            error = "Please select or enter a topic"
        else:
            try:
                post = PostService.generate_content(topic)
                has_image = PostService.generate_image_for_post(post)
                post.save()
                result = {
                    "title": post.title,
                    "has_image": has_image,
                    "post_id": post.id,
                }
                logger.info(f"User {request.user.username} generated post: {post.id}")
            except requests.exceptions.ConnectionError:
                error = "Cannot connect to AI Router at http://localhost:20128/v1. Make sure it's running."
                logger.error("AI Router connection failed")
            except Exception as e:
                error = f"Generate failed: {str(e)}"
                logger.error(f"Generate failed: {e}")
    
    context = {
        "topics": TOPICS,
        "result": result,
        "error": error,
    }
    return render(request, "generate.html", context)


@login_required
def settings_view(request):
    from django.conf import settings as django_settings
    
    ig_connection = InstagramConnectionService.get_active_connection()
    
    context = {
        "ai_api_base": django_settings.AI_API_BASE,
        "ai_model": django_settings.AI_MODEL,
        "ai_image_model": django_settings.AI_IMAGE_MODEL,
        "instagram_username": django_settings.INSTAGRAM_USERNAME,
        "db_name": django_settings.DATABASES["default"]["NAME"],
        "db_host": django_settings.DATABASES["default"]["HOST"],
        "db_port": django_settings.DATABASES["default"]["PORT"],
        "redis_url": django_settings.CELERY_BROKER_URL,
        "ig_connection": ig_connection,
    }
    return render(request, "settings.html", context)


@login_required
def test_ig_connection_view(request):
    if request.method == "POST":
        username = django_settings.INSTAGRAM_USERNAME
        success, error = InstagramConnectionService.test_connection()
        if success:
            InstagramConnectionService.mark_connected(username)
            return redirect("settings")
        else:
            InstagramConnectionService.mark_error(username, error)
            from django.contrib import messages
            messages.error(request, f"Connection failed: {error}")
            return redirect("settings")
    return redirect("settings")
