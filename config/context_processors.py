from posts.models import Post

def notification_count(request):
    """Provide notification count for the navbar badge."""
    if not request.user.is_authenticated:
        return {"notification_count": 0}
    pending = Post.objects.filter(status__in=["generated", "failed"]).count()
    return {"notification_count": pending}
