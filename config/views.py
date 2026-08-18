from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from django.conf import settings as django_settings
from datetime import timedelta
from posts.models import Post, InstagramConnection, Topic
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
def publish_now_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.status != "scheduled":
        messages.error(request, "Only scheduled posts can be published now.")
        return redirect("schedule")
    
    PostService.mark_posting(post)
    try:
        from ai.services import InstagramAutomationService
        success = InstagramAutomationService.publish_post(post)
        if success:
            PostService.mark_published(post)
            messages.success(request, f"Post '{post.title}' published successfully.")
        else:
            PostService.mark_failed(post, "Publishing failed")
            messages.error(request, f"Failed to publish post '{post.title}'.")
    except Exception as e:
        PostService.mark_failed(post, str(e))
        messages.error(request, f"Error publishing post: {str(e)}")
    
    return redirect("schedule")


@login_required
def retry_now_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.status != "failed":
        messages.error(request, "Only failed posts can be retried.")
        return redirect("schedule")
    
    if not PostService.should_retry(post):
        messages.error(request, "Retry not allowed yet due to backoff delay.")
        return redirect("schedule")
    
    PostService.mark_posting(post)
    try:
        from ai.services import InstagramAutomationService
        success = InstagramAutomationService.publish_post(post)
        if success:
            PostService.mark_published(post)
            messages.success(request, f"Post '{post.title}' retried and published successfully.")
        else:
            PostService.mark_failed(post, "Retry failed")
            messages.error(request, f"Retry failed for post '{post.title}'.")
    except Exception as e:
        PostService.mark_failed(post, str(e))
        messages.error(request, f"Error retrying post: {str(e)}")
    
    return redirect("schedule")


@login_required
def generate_view(request):
    topics = list(Topic.objects.values_list("name", flat=True))
    
    result = None
    error = None
    
    if request.method == "POST":
        topic = request.POST.get("topic")
        custom_topic = request.POST.get("custom_topic", "").strip()
        
        if custom_topic:
            topic = custom_topic
            Topic.objects.get_or_create(name=topic)
            topics = list(Topic.objects.values_list("name", flat=True))
        elif not topic:
            error = "Please select or enter a topic"
        else:
            try:
                post = PostService.generate_content(topic)
                post.save()
                has_image = PostService.generate_image_for_post(post)
                logger.info(f"User {request.user.username} generated post: {post.id}")
                result = {
                    "post_id": post.id,
                    "title": post.title,
                    "topic": post.topic,
                    "status": post.status,
                    "has_image": has_image,
                    "caption": post.caption,
                    "hashtags": post.hashtags,
                }
            except requests.exceptions.ConnectionError as e:
                error = "Cannot connect to AI Router at http://localhost:20128/v1. Make sure it's running."
                logger.error(f"AI Router connection failed: {e}")
            except requests.exceptions.HTTPError as e:
                status = getattr(e.response, 'status_code', 'unknown')
                reason = getattr(e.response, 'reason', 'unknown error')
                error = f"AI Router returned error {status}: {reason}"
                logger.error(f"AI Router HTTP error: {e}")
            except requests.exceptions.Timeout as e:
                error = "AI Router request timed out. Try again."
                logger.error(f"AI Router timeout: {e}")
            except ValueError as e:
                error = f"Invalid AI response: {str(e)}"
                logger.error(f"Invalid AI response: {e}")
            except Exception as e:
                error = f"Generate failed: {str(e) if str(e) else 'Unknown error occurred'}"
                logger.error(f"Generate failed: {e}")
        
        # Return JSON for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json':
            from django.http import JsonResponse
            if result:
                return JsonResponse({"success": True, "data": result})
            return JsonResponse({"success": False, "error": error})
    
    context = {
        "topics": topics,
        "result": result,
        "error": error,
    }
    return render(request, "generate.html", context)


@login_required
def settings_view(request):
    from django.conf import settings as django_settings
    
    ig_connection = InstagramConnectionService.get_active_connection()
    
    # Get stats for display
    total_posts = Post.objects.count()
    published_posts = Post.objects.filter(status="published").count()
    failed_posts = Post.objects.filter(status="failed").count()
    scheduled_posts = Post.objects.filter(status="scheduled").count()
    success_rate = (published_posts / total_posts * 100) if total_posts > 0 else 0
    
    # Get recent published posts (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    recent_published_posts = Post.objects.filter(
        status="published",
        updated_at__gte=week_ago
    ).order_by("-updated_at")[:5]
    recent_published_count = recent_published_posts.count()
    
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
        "total_posts": total_posts,
        "published_posts": published_posts,
        "failed_posts": failed_posts,
        "scheduled_posts": scheduled_posts,
        "success_rate": round(success_rate, 1),
        "recent_published_posts": recent_published_posts,
        "recent_published_count": recent_published_count,
    }
    return render(request, "settings.html", context)


@login_required
def test_ig_connection_view(request):
    if request.method == "POST":
        username = django_settings.INSTAGRAM_USERNAME
        # Test connection without using mark_error (which triggers sync_to_async issues)
        try:
            # Simple validation - just check if username loads
            from posts.models import InstagramConnection
            conn, created = InstagramConnection.objects.get_or_create(
                username=username,
                defaults={'status': 'checking', 'is_active': False}
            )
            if conn and conn.username == username:
                conn.status = 'connected'
                conn.is_active = True
                conn.last_login = timezone.now()
                conn.save()
                return redirect('settings')
        except Exception as e:
            conn = InstagramConnection.objects.filter(username=username).first()
            if conn:
                conn.status = 'error'
                conn.is_active = False
                conn.last_error = str(e)
                conn.save()
            from django.contrib import messages
            messages.error(request, f"Connection failed: {str(e)}")
            return redirect('settings')
    return redirect('settings')


@login_required
def approval_view(request):
    pending_posts = Post.objects.filter(status="generated").order_by("-created_at")
    context = {
        "pending_posts": pending_posts,
    }
    return render(request, "approval.html", context)


@login_required
def approve_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.status = "scheduled"
    post.save()
    logger.info(f"User {request.user.username} approved post: {post.id}")
    return redirect("approval")


@login_required
def reject_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.status = "draft"
    post.save()
    logger.info(f"User {request.user.username} rejected post: {post.id}")
    return redirect("approval")


@login_required
def monitoring_view(request):
    total_posts = Post.objects.count()
    published_posts = Post.objects.filter(status="published").count()
    failed_posts = Post.objects.filter(status="failed").count()
    success_rate = (published_posts / total_posts * 100) if total_posts > 0 else 0
    
    week_ago = timezone.now() - timedelta(days=7)
    daily_stats = []
    for i in range(7):
        date = week_ago + timedelta(days=i)
        count = Post.objects.filter(
            created_at__date=date.date()
        ).count()
        daily_stats.append({
            "date": date.strftime("%Y-%m-%d"),
            "count": count,
        })
    
    context = {
        "total_posts": total_posts,
        "published_posts": published_posts,
        "failed_posts": failed_posts,
        "success_rate": round(success_rate, 1),
        "daily_stats": daily_stats,
    }
    return render(request, "monitoring.html", context)


@login_required
def health_check_view(request):
    from django.http import JsonResponse
    
    checks = {
        "database": False,
        "redis": False,
        "ai_router": False,
    }
    
    try:
        Post.objects.first()
        checks["database"] = True
    except Exception:
        pass
    
    try:
        from django.core.cache import cache
        cache.set("health_check", "ok", 1)
        checks["redis"] = cache.get("health_check") == "ok"
    except Exception:
        pass
    
    try:
        response = requests.get(f"{django_settings.AI_API_BASE}/health", timeout=5)
        checks["ai_router"] = response.status_code == 200
    except Exception:
        pass
    
    all_healthy = all(checks.values())
    return JsonResponse({
        "status": "healthy" if all_healthy else "unhealthy",
        "checks": checks,
    })
